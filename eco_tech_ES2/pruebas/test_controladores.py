import time
import unittest

from dao.excepciones import (AutenticacionError, BaseDatosError, DuplicadoError, NoEncontradoError,
                             PermisoError, ValidacionError)

from .base_pruebas import PASS, BaseConBD


class TestEmpleadosCRUD(BaseConBD):
    def test_crud_completo(self):
        e = self.nuevo_empleado()
        self.assertEqual(self.c.empleados.obtener(e.id).nombre, "Ana Pérez")
        self.c.empleados.actualizar(e.id, nombre="Ana P.", salario_base=1500000)
        e2 = self.c.empleados.obtener(e.id)
        self.assertEqual((e2.nombre, e2.salario_base), ("Ana P.", 1500000))
        self.c.empleados.eliminar(e.id)
        with self.assertRaises(NoEncontradoError):
            self.c.empleados.obtener(e.id)

    def test_tipo_se_conserva_en_bd(self):
        e = self.nuevo_empleado(tipo="GERENTE")
        self.assertEqual(self.c.empleados.obtener(e.id).TIPO, "GERENTE")

    def test_duplicados(self):
        self.nuevo_empleado()
        with self.assertRaises(DuplicadoError):
            self.nuevo_empleado(email="otro@eco.cl")             # mismo RUT
        with self.assertRaises(DuplicadoError):
            self.nuevo_empleado(rut="7654321-6")                  # mismo correo

    def test_actualizacion_invalida_no_persiste(self):
        e = self.nuevo_empleado()
        with self.assertRaises(ValidacionError):
            self.c.empleados.actualizar(e.id, email="malo")
        with self.assertRaises(ValidacionError):
            self.c.empleados.actualizar(e.id, activo=False)       # campo no editable
        self.assertEqual(self.c.empleados.obtener(e.id).email, "ana@eco.cl")

    def test_baja_logica_y_busqueda(self):
        e = self.nuevo_empleado()
        self.c.empleados.dar_de_baja(e.id)
        self.assertEqual(self.c.empleados.listar(), [])
        self.assertEqual(len(self.c.empleados.listar(solo_activos=False)), 1)
        self.assertEqual(len(self.c.empleados.buscar("Ana")), 1)
        with self.assertRaises(ValidacionError):
            self.c.empleados.buscar("a")

    def test_departamento_inexistente(self):
        with self.assertRaises(NoEncontradoError):
            self.c.empleados.registrar("PLANTA", "12345678-5", "Ana", "a@b.cl", 1000, id_departamento=999)

    def test_inyeccion_sql_se_trata_como_texto(self):
        self.nuevo_empleado()
        self.assertEqual(self.c.empleados.buscar("' OR '1'='1"), [])
        self.assertEqual(len(self.c.empleados.listar()), 1)

    def test_planilla(self):
        self.nuevo_empleado()
        self.nuevo_empleado(rut="7654321-6", email="b@eco.cl", tipo="GERENTE")
        self.assertAlmostEqual(self.c.empleados.costo_planilla(), 1_000_000 + 1_200_000)

    def test_departamentos(self):
        self.assertGreaterEqual(len(self.c.departamentos.listar()), 4)
        d = self.c.departamentos.crear("Legal", "Asesoría")
        e = self.c.empleados.registrar("PLANTA", "12345678-5", "Ana", "a@b.cl", 1000, id_departamento=d.id)
        with self.assertRaises(BaseDatosError):                   # RESTRICT
            self.c.departamentos.eliminar(d.id)
        self.assertEqual(dict((x.id, n) for x, n in self.c.departamentos.listar_con_dotacion())[d.id], 1)
        self.c.empleados.eliminar(e.id)
        self.c.departamentos.eliminar(d.id)


class TestProyectosAsignacionesHoras(BaseConBD):
    def setUp(self):
        super().setUp()
        self.emp = self.nuevo_empleado()
        self.proy = self.nuevo_proyecto()
        self.asig = self.c.asignaciones.asignar(self.emp.id, self.proy.id, "Desarrollador", 40)

    def test_asignacion_unica(self):
        with self.assertRaises(DuplicadoError):
            self.c.asignaciones.asignar(self.emp.id, self.proy.id, "Otro", 10)

    def test_no_asigna_a_proyecto_finalizado_ni_empleado_de_baja(self):
        p2 = self.nuevo_proyecto("Otro")
        self.c.proyectos.actualizar(p2.id, estado="FINALIZADO")
        with self.assertRaises(ValidacionError):
            self.c.asignaciones.asignar(self.emp.id, p2.id, "Dev", 5)
        e2 = self.nuevo_empleado("7654321-6", "b@eco.cl")
        self.c.empleados.dar_de_baja(e2.id)
        with self.assertRaises(ValidacionError):
            self.c.asignaciones.asignar(e2.id, self.proy.id, "Dev", 5)

    def test_horas_y_limite(self):
        for dia in ("01", "02", "03"):
            self.c.registros.registrar(self.asig.id, f"2026-02-{dia}", 10, "Backend")   # 30 h
        with self.assertRaises(ValidacionError):
            self.c.registros.registrar(self.asig.id, "2026-02-04", 11)                  # 30 + 11 > 40
        self.c.registros.registrar(self.asig.id, "2026-02-04", 10)
        self.assertEqual(sum(r.horas for r in self.c.registros.listar_por_asignacion(self.asig.id)), 40)

    def test_reportes(self):
        self.c.registros.registrar(self.asig.id, "2026-02-01", 8)
        rp = self.c.registros.reporte_horas_por_proyecto()
        self.assertEqual((rp[0]["horas"], rp[0]["horas_asignadas"]), (8, 40))
        self.assertEqual(self.c.registros.reporte_horas_por_empleado()[0]["horas"], 8)

    def test_cascada_y_restrict(self):
        self.c.registros.registrar(self.asig.id, "2026-02-01", 8)
        with self.assertRaises(BaseDatosError):                    # proyecto con asignaciones
            self.c.proyectos.eliminar(self.proy.id)
        self.c.asignaciones.eliminar(self.asig.id)                 # borra también las horas
        self.assertEqual(self.cx.consultar_uno("SELECT COUNT(*) n FROM registro_tiempo")["n"], 0)
        self.c.proyectos.eliminar(self.proy.id)


class TestSeguridad(BaseConBD):
    def test_login_y_mensaje_generico(self):
        self.c.auth.cerrar_sesion()
        for u, p in (("admin", "mala"), ("fantasma", PASS)):
            with self.assertRaises(AutenticacionError) as cm:
                self.c.auth.iniciar_sesion(u, p)
            self.assertEqual(str(cm.exception), "Usuario o contraseña incorrectos.")

    def test_bloqueo_tras_intentos(self):
        self.c.auth.cerrar_sesion()
        for _ in range(3):
            with self.assertRaises(AutenticacionError):
                self.c.auth.iniciar_sesion("admin", "mala")
        with self.assertRaises(AutenticacionError) as cm:
            self.c.auth.iniciar_sesion("admin", PASS)               # correcta, pero bloqueada
        self.assertIn("bloqueada", str(cm.exception))
        self.c.auth.BLOQUEO_SEG = 0                                  # expira el bloqueo
        self.c.auth.iniciar_sesion("admin", PASS)

    def test_primer_admin_solo_una_vez(self):
        with self.assertRaises(ValidacionError):
            self.c.auth.registrar_primer_admin("otro", PASS)

    def test_sin_sesion_no_opera(self):
        self.c.auth.cerrar_sesion()
        with self.assertRaises(PermisoError):
            self.c.empleados.listar()

    def test_permisos_por_rol(self):
        emp = self.nuevo_empleado()
        otro = self.nuevo_empleado("7654321-6", "b@eco.cl")
        proy = self.nuevo_proyecto()
        mia = self.c.asignaciones.asignar(emp.id, proy.id, "Dev", 20)
        ajena = self.c.asignaciones.asignar(otro.id, proy.id, "QA", 20)
        self.c.usuarios.crear("ana", PASS, "EMPLEADO", emp.id)
        self.c.usuarios.crear("jefe", PASS, "GERENTE")

        self.entrar("ana")
        self.assertEqual(len(self.c.asignaciones.listar_mias()), 1)
        self.c.registros.registrar(mia.id, "2026-02-01", 5)
        for accion in (lambda: self.c.empleados.listar(), lambda: self.c.usuarios.listar(),
                       lambda: self.c.registros.registrar(ajena.id, "2026-02-01", 5),
                       lambda: self.c.registros.reporte_horas_por_proyecto(),
                       lambda: self.c.proyectos.eliminar(proy.id)):
            with self.assertRaises(PermisoError):
                accion()

        self.entrar("jefe")
        self.assertEqual(len(self.c.empleados.listar()), 2)
        with self.assertRaises(PermisoError):
            self.c.empleados.eliminar(emp.id)                        # solo ADMIN
        with self.assertRaises(PermisoError):
            self.c.usuarios.crear("x1234", PASS, "ADMIN")

    def test_reglas_de_usuarios(self):
        with self.assertRaises(ValidacionError):
            self.c.usuarios.crear("sinemp", PASS, "EMPLEADO")        # EMPLEADO requiere empleado
        admin = self.c.sesion.usuario
        with self.assertRaises(ValidacionError):
            self.c.usuarios.cambiar_estado(admin.id, False)          # no auto-desactivarse
        with self.assertRaises(ValidacionError):
            self.c.usuarios.eliminar(admin.id)

    def test_cambio_de_password(self):
        with self.assertRaises(AutenticacionError):
            self.c.auth.cambiar_mi_password("incorrecta", "Nueva12345")
        with self.assertRaises(ValidacionError):
            self.c.auth.cambiar_mi_password(PASS, "corta")
        self.c.auth.cambiar_mi_password(PASS, "Nueva12345")
        self.entrar("admin", "Nueva12345")


if __name__ == "__main__":
    unittest.main()
