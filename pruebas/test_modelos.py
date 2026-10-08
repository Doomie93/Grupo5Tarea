import unittest
from datetime import date, timedelta

from dao.excepciones import ValidacionError
from modelo import parsear_fecha, validar_rut
from modelo.empleado import Empleado, EmpleadoHonorarios, EmpleadoPlanta, Gerente, crear_empleado
from modelo.proyecto import Proyecto
from modelo.registro_tiempo import RegistroTiempo
from modelo.usuario import Usuario, hashear_password, verificar_password

A = dict(rut="12345678-5", nombre="Ana Pérez", email="ana@eco.cl", salario_base=1_000_000)


class TestEmpleado(unittest.TestCase):
    def test_clase_abstracta(self):
        with self.assertRaises(TypeError):
            Empleado(**A)

    def test_polimorfismo(self):
        self.assertEqual(EmpleadoPlanta(**A).calcular_salario(), 1_000_000)
        self.assertAlmostEqual(EmpleadoHonorarios(**A).calcular_salario(), 862_500)
        self.assertAlmostEqual(Gerente(**A).calcular_salario(), 1_200_000)

    def test_fabrica(self):
        self.assertIsInstance(crear_empleado("gerente", **A), Gerente)
        with self.assertRaises(ValidacionError):
            crear_empleado("ALIEN", **A)

    def test_validaciones(self):
        malos = [dict(rut="mal"), dict(rut="12345678-9"), dict(nombre="A"), dict(email="x"),
                 dict(salario_base=-1), dict(salario_base="abc"), dict(salario_base=0),
                 dict(fecha_ingreso=date.today() + timedelta(days=1)), dict(fecha_ingreso="2026-13-45")]
        for cambio in malos:
            with self.subTest(cambio), self.assertRaises(ValidacionError):
                EmpleadoPlanta(**{**A, **cambio})

    def test_antiguedad(self):
        e = EmpleadoPlanta(**A, fecha_ingreso=date.today().replace(year=date.today().year - 3))
        self.assertEqual(e.antiguedad_anios(), 3)

    def test_rut_normaliza(self):
        self.assertEqual(validar_rut("12.345.678-5"), "12345678-5")
        self.assertEqual(validar_rut("7654321-6"), "7654321-6")


class TestUsuario(unittest.TestCase):
    def test_hash_no_es_texto_plano(self):
        u = Usuario.nuevo("Carlos", "Clave1234", "ADMIN")
        self.assertNotIn("Clave1234", u.password_hash)
        self.assertEqual(u.username, "carlos")
        self.assertTrue(u.autenticar("Clave1234"))
        self.assertFalse(u.autenticar("otra"))

    def test_sal_distinta(self):
        self.assertNotEqual(hashear_password("Clave1234"), hashear_password("Clave1234"))
        self.assertFalse(verificar_password("x", "basura"))

    def test_politica_password_y_rol(self):
        for pw in ("corta1", "sololetras", "12345678"):
            with self.assertRaises(ValidacionError):
                Usuario.nuevo("user1", pw, "ADMIN")
        with self.assertRaises(ValidacionError):
            Usuario.nuevo("user1", "Clave1234", "SUPERMAN")
        with self.assertRaises(ValidacionError):
            Usuario.nuevo("a b", "Clave1234", "ADMIN")


class TestProyectoYRegistro(unittest.TestCase):
    def test_fechas_coherentes(self):
        with self.assertRaises(ValidacionError):
            Proyecto("Proyecto X", "2026-05-01", fecha_fin="2026-04-01")
        p = Proyecto("Proyecto X", "2026-05-01", fecha_fin="2026-06-01")
        with self.assertRaises(ValidacionError):
            p.fecha_fin = "2026-01-01"

    def test_estado_y_asignaciones(self):
        p = Proyecto("Proyecto X", "2026-05-01")
        self.assertTrue(p.acepta_asignaciones())
        p.estado = "finalizado"
        self.assertFalse(p.acepta_asignaciones())
        with self.assertRaises(ValidacionError):
            p.estado = "NADA"

    def test_registro_horas(self):
        for horas in (0, -2, 25, "x"):
            with self.assertRaises(ValidacionError):
                RegistroTiempo(1, "2026-01-01", horas)
        with self.assertRaises(ValidacionError):
            RegistroTiempo(1, date.today() + timedelta(days=2), 3)

    def test_parsear_fecha(self):
        self.assertIsNone(parsear_fecha("", opcional=True))
        with self.assertRaises(ValidacionError):
            parsear_fecha("")


if __name__ == "__main__":
    unittest.main()
