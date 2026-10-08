"""Interfaz de consola: solo muestra información y pide datos.
Toda la lógica de negocio vive en los controladores."""
from dao.excepciones import AutenticacionError, EcoTechError
from modelo.empleado import TIPOS_EMPLEADO
from modelo.proyecto import ESTADOS
from modelo.usuario import ADMIN, EMPLEADO, GERENTE, ROLES
from modelo import validar_email, validar_rut

from . import validaciones as v


# ---------------------------------------------------------------- utilidades
def titulo(txt):
    print(f"\n{'=' * 60}\n  {txt}\n{'=' * 60}")


def tabla(encabezados, filas):
    filas = [[str(c) for c in f] for f in filas]
    if not filas:
        print("  (sin resultados)")
        return
    anchos = [max(len(h), *(len(f[i]) for f in filas)) for i, h in enumerate(encabezados)]
    linea = "  " + "  ".join(h.ljust(a) for h, a in zip(encabezados, anchos))
    print(linea)
    print("  " + "  ".join("-" * a for a in anchos))
    for f in filas:
        print("  " + "  ".join(c.ljust(a) for c, a in zip(f, anchos)))


def seguro(accion):
    """Ejecuta una acción de menú: los errores esperados se informan sin cerrar el programa."""
    try:
        accion()
    except EcoTechError as e:
        print(f"\n⚠  {e}")
    except KeyboardInterrupt:
        print("\n   Operación cancelada.")


def dinero(x):
    return f"${x:,.0f}".replace(",", ".")


# ---------------------------------------------------------------- aplicación
class AplicacionConsola:
    def __init__(self, ctx):
        self.c = ctx  # contenedor de controladores (ver main.py)

    # ---- arranque / login ----
    def ejecutar(self):
        titulo("EcoTech Solutions · Sistema de Gestión")
        try:
            if not self.c.auth.hay_usuarios():
                self._crear_primer_admin()
            while True:
                if not self._login():
                    break
                self._menu_principal()
        except EOFError:
            print("\nEntrada finalizada.")
        print("Hasta luego.")

    def _crear_primer_admin(self):
        print("\nPrimer uso: cree la cuenta de administrador.")
        while True:
            try:
                u = v.pedir_texto("Usuario", 3, 30)
                self.c.auth.registrar_primer_admin(u, v.pedir_password("Contraseña (mín. 8, letras y números)"))
                print("✓ Administrador creado.")
                return
            except EcoTechError as e:
                print(f"⚠  {e}")

    def _login(self):
        print("\n--- Inicio de sesión (Enter vacío para salir) ---")
        while True:
            usuario = input("Usuario: ").strip()
            if not usuario:
                return False
            try:
                u = self.c.auth.iniciar_sesion(usuario, v.pedir_password())
                print(f"\n✓ Bienvenido/a, {u.username} ({u.rol})")
                return True
            except AutenticacionError as e:
                print(f"⚠  {e}")

    # ---- menú principal por rol ----
    def _menu_principal(self):
        rol = self.c.sesion.usuario.rol
        opciones = {
            ADMIN: [("Empleados", self.menu_empleados), ("Departamentos", self.menu_departamentos),
                    ("Proyectos", self.menu_proyectos), ("Asignaciones", self.menu_asignaciones),
                    ("Registro de horas", self.menu_horas), ("Reportes", self.menu_reportes),
                    ("Usuarios", self.menu_usuarios)],
            GERENTE: [("Empleados", self.menu_empleados), ("Departamentos", self.menu_departamentos),
                      ("Proyectos", self.menu_proyectos), ("Asignaciones", self.menu_asignaciones),
                      ("Registro de horas", self.menu_horas), ("Reportes", self.menu_reportes)],
            EMPLEADO: [("Mis asignaciones", lambda: self._ver_mis_asignaciones()),
                       ("Registrar / ver mis horas", self.menu_horas)],
        }[rol]
        opciones = opciones + [("Cambiar mi contraseña", self._cambiar_password)]
        while True:
            titulo(f"Menú principal · {self.c.sesion.usuario.username} ({rol})")
            for i, (nombre, _) in enumerate(opciones, 1):
                print(f"  {i}. {nombre}")
            print("  0. Cerrar sesión")
            op = v.pedir_entero("Opción", 0, len(opciones))
            if op == 0:
                self.c.auth.cerrar_sesion()
                return
            seguro(opciones[op - 1][1])

    @staticmethod
    def _submenu(nombre, acciones):
        while True:
            titulo(nombre)
            for i, (txt, _) in enumerate(acciones, 1):
                print(f"  {i}. {txt}")
            print("  0. Volver")
            op = v.pedir_entero("Opción", 0, len(acciones))
            if op == 0:
                return
            seguro(acciones[op - 1][1])

    # ---------------------------------------------------------- EMPLEADOS
    def menu_empleados(self):
        a = [("Registrar empleado", self._emp_registrar), ("Listar empleados activos", self._emp_listar),
             ("Buscar (nombre / RUT / correo)", self._emp_buscar), ("Ver detalle", self._emp_detalle),
             ("Actualizar datos", self._emp_actualizar), ("Dar de baja", self._emp_baja),
             ("Reactivar", self._emp_reactivar), ("Eliminar definitivamente", self._emp_eliminar),
             ("Costo total de planilla", self._emp_planilla)]
        self._submenu("Gestión de empleados", a)

    def _mostrar_empleados(self, empleados):
        tabla(["ID", "Tipo", "RUT", "Nombre", "Correo", "Líquido est.", "Depto", "Estado"],
              [(e.id, e.TIPO, e.rut, e.nombre, e.email, dinero(e.calcular_salario()),
                e.id_departamento or "-", "Activo" if e.activo else "Baja") for e in empleados])

    def _emp_registrar(self):
        self._listar_deptos_simple()
        tipo = v.pedir_opcion("Tipo", list(TIPOS_EMPLEADO))
        rut = v.pedir_con("RUT (12345678-5)", validar_rut)
        nombre = v.pedir_texto("Nombre completo", 2, 80)
        email = v.pedir_con("Correo", validar_email)
        salario = v.pedir_decimal("Salario base", 0, 1e9, estricto=True)
        ingreso = v.pedir_fecha("Fecha de ingreso", opcional=True)
        depto = self._pedir_depto_opcional()
        e = self.c.empleados.registrar(tipo, rut, nombre, email, salario, ingreso, depto)
        print(f"✓ Empleado registrado con ID {e.id}.")

    def _pedir_depto_opcional(self, defecto=None):
        txt = input("ID de departamento (Enter = " + ("mantener" if defecto else "ninguno") + "): ").strip()
        if not txt:
            return defecto
        while not txt.isdigit():
            txt = input("   ✗ Debe ser numérico. ID de departamento: ").strip()
        return int(txt)

    def _emp_listar(self):
        self._mostrar_empleados(self.c.empleados.listar())

    def _emp_buscar(self):
        self._mostrar_empleados(self.c.empleados.buscar(input("Texto a buscar: ")))

    def _emp_detalle(self):
        e = self.c.empleados.obtener(v.pedir_entero("ID del empleado", 1))
        print(f"\n  {e.nombre} · {e.TIPO}\n  RUT: {e.rut}   Correo: {e.email}"
              f"\n  Salario base: {dinero(e.salario_base)}   Líquido estimado: {dinero(e.calcular_salario())}"
              f"\n  Ingreso: {e.fecha_ingreso}  ({e.antiguedad_anios()} años)   Estado: "
              f"{'Activo' if e.activo else 'De baja'}")

    def _emp_actualizar(self):
        e = self.c.empleados.obtener(v.pedir_entero("ID a actualizar", 1))
        print("  (Enter conserva el valor actual)")
        campos = {
            "nombre": v.pedir_texto("Nombre", 2, 80, defecto=e.nombre),
            "email": v.pedir_con("Correo", validar_email, defecto=e.email),
            "salario_base": v.pedir_decimal("Salario base", 0, 1e9, True, defecto=e.salario_base),
            "id_departamento": self._pedir_depto_opcional(e.id_departamento),
        }
        self.c.empleados.actualizar(e.id, **campos)
        print("✓ Empleado actualizado.")

    def _emp_baja(self):
        id_ = v.pedir_entero("ID a dar de baja", 1)
        if v.confirmar("¿Confirma la baja? (se conserva su historial)"):
            self.c.empleados.dar_de_baja(id_)
            print("✓ Empleado dado de baja.")

    def _emp_reactivar(self):
        self.c.empleados.reactivar(v.pedir_entero("ID a reactivar", 1))
        print("✓ Empleado reactivado.")

    def _emp_eliminar(self):
        id_ = v.pedir_entero("ID a eliminar", 1)
        if v.confirmar("⚠ Eliminación DEFINITIVA. ¿Continuar?"):
            self.c.empleados.eliminar(id_)
            print("✓ Empleado eliminado.")

    def _emp_planilla(self):
        print(f"  Costo mensual estimado de planilla activa: {dinero(self.c.empleados.costo_planilla())}")

    # ------------------------------------------------------ DEPARTAMENTOS
    def menu_departamentos(self):
        self._submenu("Departamentos", [
            ("Crear", self._dep_crear), ("Listar (con dotación)", self._dep_listar),
            ("Actualizar", self._dep_actualizar), ("Eliminar", self._dep_eliminar)])

    def _listar_deptos_simple(self):
        try:
            print("  Departamentos:", "; ".join(str(d) for d in self.c.departamentos.listar()) or "(ninguno)")
        except EcoTechError:
            pass

    def _dep_crear(self):
        d = self.c.departamentos.crear(v.pedir_texto("Nombre", 2, 60), v.pedir_texto_opcional("Descripción"))
        print(f"✓ Departamento creado con ID {d.id}.")

    def _dep_listar(self):
        tabla(["ID", "Nombre", "Descripción", "Empleados"],
              [(d.id, d.nombre, d.descripcion, n) for d, n in self.c.departamentos.listar_con_dotacion()])

    def _dep_actualizar(self):
        id_ = v.pedir_entero("ID a actualizar", 1)
        self.c.departamentos.actualizar(id_, v.pedir_texto_opcional("Nuevo nombre") or None,
                                        v.pedir_texto_opcional("Nueva descripción") or None)
        print("✓ Departamento actualizado.")

    def _dep_eliminar(self):
        id_ = v.pedir_entero("ID a eliminar", 1)
        if v.confirmar("¿Eliminar departamento?"):
            self.c.departamentos.eliminar(id_)
            print("✓ Departamento eliminado.")

    # ----------------------------------------------------------- PROYECTOS
    def menu_proyectos(self):
        self._submenu("Proyectos", [
            ("Crear", self._pro_crear), ("Listar", self._pro_listar),
            ("Cambiar estado", self._pro_estado), ("Actualizar datos", self._pro_actualizar),
            ("Eliminar", self._pro_eliminar)])

    def _pro_crear(self):
        p = self.c.proyectos.crear(
            v.pedir_texto("Nombre del proyecto", 3, 80), v.pedir_fecha("Fecha de inicio"),
            v.pedir_texto_opcional("Descripción"), v.pedir_fecha("Fecha de término", opcional=True),
            v.pedir_decimal("Presupuesto", 0, 1e12))
        print(f"✓ Proyecto creado con ID {p.id}.")

    def _pro_listar(self):
        tabla(["ID", "Nombre", "Estado", "Inicio", "Término", "Presupuesto"],
              [(p.id, p.nombre, p.estado, p.fecha_inicio, p.fecha_fin or "-", dinero(p.presupuesto))
               for p in self.c.proyectos.listar()])

    def _pro_estado(self):
        id_ = v.pedir_entero("ID del proyecto", 1)
        self.c.proyectos.actualizar(id_, estado=v.pedir_opcion("Nuevo estado", list(ESTADOS)))
        print("✓ Estado actualizado.")

    def _pro_actualizar(self):
        p = self.c.proyectos.obtener(v.pedir_entero("ID a actualizar", 1))
        self.c.proyectos.actualizar(
            p.id, nombre=v.pedir_texto("Nombre", 3, 80, defecto=p.nombre),
            descripcion=v.pedir_texto_opcional("Descripción", p.descripcion),
            presupuesto=v.pedir_decimal("Presupuesto", 0, 1e12, defecto=p.presupuesto))
        print("✓ Proyecto actualizado.")

    def _pro_eliminar(self):
        id_ = v.pedir_entero("ID a eliminar", 1)
        if v.confirmar("¿Eliminar proyecto?"):
            self.c.proyectos.eliminar(id_)
            print("✓ Proyecto eliminado.")

    # --------------------------------------------------------- ASIGNACIONES
    def menu_asignaciones(self):
        self._submenu("Asignaciones empleado-proyecto", [
            ("Asignar empleado a proyecto", self._asi_crear), ("Listar asignaciones", self._asi_listar),
            ("Modificar rol / horas", self._asi_actualizar), ("Eliminar asignación", self._asi_eliminar)])

    def _tabla_asignaciones(self, filas):
        tabla(["ID", "Empleado", "Proyecto", "Rol", "H. asignadas", "H. registradas"],
              [(f["id"], f["empleado"], f["proyecto"], f["rol_proyecto"],
                f"{f['horas_asignadas']:g}", f"{f['horas_registradas']:g}") for f in filas])

    def _asi_crear(self):
        a = self.c.asignaciones.asignar(
            v.pedir_entero("ID del empleado", 1), v.pedir_entero("ID del proyecto", 1),
            v.pedir_texto("Rol en el proyecto", 2, 60), v.pedir_decimal("Horas asignadas", 0, 10000, True))
        print(f"✓ Asignación creada con ID {a.id}.")

    def _asi_listar(self):
        self._tabla_asignaciones(self.c.asignaciones.listar())

    def _ver_mis_asignaciones(self):
        self._tabla_asignaciones(self.c.asignaciones.listar_mias())

    def _asi_actualizar(self):
        id_ = v.pedir_entero("ID de la asignación", 1)
        rol = v.pedir_texto_opcional("Nuevo rol")
        horas = v.pedir_decimal("Nuevas horas", 0, 10000, True, defecto=0)
        self.c.asignaciones.actualizar(id_, rol or None, horas or None)
        print("✓ Asignación actualizada.")

    def _asi_eliminar(self):
        id_ = v.pedir_entero("ID a eliminar", 1)
        if v.confirmar("Se borrarán también sus horas registradas. ¿Continuar?"):
            self.c.asignaciones.eliminar(id_)
            print("✓ Asignación eliminada.")

    # --------------------------------------------------------------- HORAS
    def menu_horas(self):
        self._submenu("Registro de horas", [
            ("Registrar horas", self._hor_registrar), ("Ver horas de una asignación", self._hor_listar),
            ("Eliminar un registro", self._hor_eliminar)])

    def _hor_registrar(self):
        if self.c.sesion.usuario.rol == EMPLEADO:
            self._ver_mis_asignaciones()
        r = self.c.registros.registrar(
            v.pedir_entero("ID de la asignación", 1), v.pedir_fecha("Fecha"),
            v.pedir_decimal("Horas trabajadas", 0, 24, True), v.pedir_texto_opcional("Descripción"))
        print(f"✓ Registro guardado (ID {r.id}).")

    def _hor_listar(self):
        regs = self.c.registros.listar_por_asignacion(v.pedir_entero("ID de la asignación", 1))
        tabla(["ID", "Fecha", "Horas", "Descripción"], [(r.id, r.fecha, f"{r.horas:g}", r.descripcion) for r in regs])
        print(f"  Total: {sum(r.horas for r in regs):g} h")

    def _hor_eliminar(self):
        id_ = v.pedir_entero("ID del registro", 1)
        if v.confirmar("¿Eliminar registro?"):
            self.c.registros.eliminar(id_)
            print("✓ Registro eliminado.")

    # ------------------------------------------------------------ REPORTES
    def menu_reportes(self):
        self._submenu("Reportes", [("Horas por proyecto", self._rep_proyecto),
                                   ("Horas por empleado", self._rep_empleado)])

    def _rep_proyecto(self):
        tabla(["Proyecto", "Estado", "H. asignadas", "H. registradas", "Avance"],
              [(f["proyecto"], f["estado"], f"{f['horas_asignadas']:g}", f"{f['horas']:g}",
                f"{(f['horas'] / f['horas_asignadas'] * 100):.0f}%" if f["horas_asignadas"] else "-")
               for f in self.c.registros.reporte_horas_por_proyecto()])

    def _rep_empleado(self):
        tabla(["Empleado", "Horas registradas"],
              [(f["empleado"], f"{f['horas']:g}") for f in self.c.registros.reporte_horas_por_empleado()])

    # ------------------------------------------------------------ USUARIOS
    def menu_usuarios(self):
        self._submenu("Usuarios del sistema", [
            ("Crear usuario", self._usr_crear), ("Listar", self._usr_listar),
            ("Activar / desactivar", self._usr_estado), ("Eliminar", self._usr_eliminar)])

    def _usr_crear(self):
        rol = v.pedir_opcion("Rol", list(ROLES))
        id_emp = v.pedir_entero("ID de empleado vinculado", 1) if rol == EMPLEADO else None
        u = self.c.usuarios.crear(v.pedir_texto("Usuario", 3, 30),
                                  v.pedir_password("Contraseña (mín. 8, letras y números)"), rol, id_emp)
        print(f"✓ Usuario creado con ID {u.id}.")

    def _usr_listar(self):
        tabla(["ID", "Usuario", "Rol", "Empleado", "Activo"],
              [(u.id, u.username, u.rol, u.id_empleado or "-", "Sí" if u.activo else "No")
               for u in self.c.usuarios.listar()])

    def _usr_estado(self):
        id_ = v.pedir_entero("ID del usuario", 1)
        self.c.usuarios.cambiar_estado(id_, v.confirmar("¿Dejarlo ACTIVO?"))
        print("✓ Estado actualizado.")

    def _usr_eliminar(self):
        id_ = v.pedir_entero("ID a eliminar", 1)
        if v.confirmar("¿Eliminar usuario?"):
            self.c.usuarios.eliminar(id_)
            print("✓ Usuario eliminado.")

    # ------------------------------------------------------- CONTRASEÑA
    def _cambiar_password(self):
        self.c.auth.cambiar_mi_password(v.pedir_password("Contraseña actual"),
                                        v.pedir_password("Nueva contraseña"))
        print("✓ Contraseña actualizada.")
