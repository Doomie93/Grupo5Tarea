import sys
import logging
from datetime import date
from controlador.dto_departamento import DepartamentoDTO
from controlador.dto_empleado import EmpleadoDTO
from controlador.dto_proyecto import ProyectoDTO
from controlador.dto_asignacion import AsignacionProyectoDTO
from controlador.dto_registro import RegistroTiempoDTO
from controlador.dto_usuario import UsuarioDTO
from controlador import permisos, sesion
from vista.entrada import pedir, pedirClave, MSG_ATAJO, OperacionCancelada
from vista.validaciones import (validaInt, validaTexto, validaCorreo, validaTelefono, validaFecha,
                                validaNombreUsuario, validaClaveNueva, validaConfirmacion, validaOpc)

log = logging.getLogger("ecotech")


# ------------------------------------------------------------------ utilidades
def titulo(txt: str) -> None:
    print("\n--------------------")
    print(txt)
    print("--------------------\n")


def listar(lista: list, vacio: str) -> None:
    if len(lista) > 0:
        for item in lista:
            print(item)
    else:
        print(vacio)


def probarConexion() -> bool:
    return UsuarioDTO().probarConexion()


# Carga las listas de clase desde la BD (en este orden por las relaciones entre objetos)
def cargaInicial() -> None:
    deptoDTO = DepartamentoDTO()
    deptoDTO.cargarDatos()
    EmpleadoDTO().cifrarPendientes()      # cifra correo/sueldo/dirección/teléfono que hayan quedado en claro en la BD
    EmpleadoDTO().cargarDatos()
    deptoDTO.vincularGerentes()
    ProyectoDTO().cargarDatos()
    AsignacionProyectoDTO().cargarDatos()
    RegistroTiempoDTO().cargarDatos()


# Login: la contraseña se oculta con "*"
def validarLogin():
    nombre = pedir("Ingrese usuario (escriba 'cancelar' para cerrar el programa): ").strip()
    clave = pedirClave("Ingrese contraseña (ENTER vacío para cerrar el programa): ")
    return UsuarioDTO().validarAcceso(nombre, clave)


# Selectores de objetos (retornan None si no existen)
def seleccionarDepto(txt: str = "Id del departamento"):
    depto = DepartamentoDTO().findDepto(validaInt(txt, 1))
    if depto is None:
        print("El departamento no existe.")
    return depto


def seleccionarEmpleado(txt: str = "Id del empleado"):
    emp = EmpleadoDTO().findEmpleado(validaInt(txt, 1))
    if emp is None:
        print("El empleado no existe.")
    return emp


def seleccionarProyecto(txt: str = "Id del proyecto"):
    proy = ProyectoDTO().findProyecto(validaInt(txt, 1))
    if proy is None:
        print("El proyecto no existe.")
    return proy


# ------------------------------------------------------------------ departamentos
def registrarDepto() -> None:
    titulo("Agregar Departamento.")
    nombre = validaTexto("Nombre del departamento", 3, 50)
    idGerente = None
    if validaConfirmacion("¿Desea asignar un gerente?"):
        gerente = seleccionarEmpleado("Id del empleado gerente")
        if gerente is None:
            return print("Operación Cancelada.")
        idGerente = gerente.getId()
    print(DepartamentoDTO().addDepto(nombre, idGerente))


def modificarDepto() -> None:
    titulo("Modificar Departamento.")
    depto = seleccionarDepto()
    if depto is None:
        return
    nombre = validaTexto("Nombre del departamento", 3, 50, actual=depto.getNombre())
    idGerente = depto.getGerente().getId() if depto.getGerente() is not None else None
    if validaConfirmacion("¿Desea cambiar el gerente?"):
        gerente = seleccionarEmpleado("Id del nuevo gerente")
        if gerente is None:
            return print("Operación Cancelada.")
        idGerente = gerente.getId()
    print(DepartamentoDTO().updateDepto(depto.getId(), nombre, idGerente))


def eliminarDepto() -> None:
    titulo("Eliminar Departamento.")
    depto = seleccionarDepto()
    if depto is None:
        return
    if len(depto.getEmpleados()) > 0:
        return print(f"No se puede eliminar: el departamento tiene {len(depto.getEmpleados())} empleado(s). "
                     "Reasígnelos a otro departamento antes de eliminarlo.")
    if validaConfirmacion("¿Estas seguro que deseas eliminar el Departamento?"):
        print(DepartamentoDTO().delDepto(depto.getId()))
    else:
        print("Operación Cancelada.")


def mostrarDeptos() -> None:
    titulo("Listado de Departamentos.")
    listar(DepartamentoDTO().findAllDeptos(), "No hay Departamentos Registrados.")


def buscarDepto() -> None:
    titulo("Buscar Departamento.")
    depto = seleccionarDepto()
    if depto is not None:
        print(depto)
        print("\nEmpleados del departamento:")
        listar(depto.getEmpleados(), "El departamento no tiene empleados.")


def agregarEmpleadoDepto() -> None:
    titulo("Agregar Empleado a un Departamento.")
    emp = seleccionarEmpleado()
    if emp is None:
        return
    if emp.getDepartamento() is not None:
        return print(f"El empleado ya pertenece a '{emp.getDepartamento().getNombre()}', use la opción Reasignar.")
    depto = seleccionarDepto()
    if depto is not None:
        print(DepartamentoDTO().addEmpleadoDepto(emp.getId(), depto.getId()))


def reasignarEmpleadoDepto() -> None:
    titulo("Reasignar Empleado a otro Departamento.")
    emp = seleccionarEmpleado()
    if emp is None:
        return
    if emp.getDepartamento() is None:
        return print("El empleado no tiene departamento, use la opción Agregar Empleado.")
    depto = seleccionarDepto("Id del nuevo departamento")
    if depto is None:
        return
    if depto.getId() == emp.getDepartamento().getId():
        return print("El empleado ya pertenece a ese departamento.")
    print(DepartamentoDTO().reasignarEmpleadoDepto(emp.getId(), depto.getId()))


# ------------------------------------------------------------------ empleados
def registrarEmpleado() -> None:
    titulo("Agregar Empleado.")
    nombre = validaTexto("Nombre", 2, 50)
    apellido = validaTexto("Apellido", 2, 50)
    correo = validaCorreo()
    fecha = validaFecha("Fecha de contrato", permitirFutura=False)
    salario = validaInt("Salario (pesos)", 0)
    direccion = validaTexto("Dirección", 3, 100)
    telefono = validaTelefono()
    idDepto = None
    if validaConfirmacion("¿Desea asignar un departamento ahora?"):
        depto = seleccionarDepto()
        if depto is None:
            return print("Operación Cancelada.")
        idDepto = depto.getId()
    print(EmpleadoDTO().addEmpleado(nombre, apellido, correo, fecha, salario, direccion, telefono, idDepto))


def modificarEmpleado() -> None:
    titulo("Modificar Empleado.")
    emp = seleccionarEmpleado()
    if emp is None:
        return
    nombre = validaTexto("Nombre", 2, 50, actual=emp.getNombre())
    apellido = validaTexto("Apellido", 2, 50, actual=emp.getApellido())
    correo = validaCorreo(emp.getCorreo())
    fecha = validaFecha("Fecha de contrato", actual=emp.getFechaContrato(), permitirFutura=False)
    salario = validaInt("Salario (pesos)", 0, actual=emp.getSalario())
    direccion = validaTexto("Dirección", 3, 100, actual=emp.getDireccion())
    telefono = validaTelefono(emp.getTelefono())
    print(EmpleadoDTO().updateEmpleado(emp.getId(), nombre, apellido, correo, fecha, salario, direccion, telefono))


def eliminarEmpleado() -> None:
    titulo("Eliminar Empleado.")
    emp = seleccionarEmpleado()
    if emp is None:
        return
    if validaConfirmacion("¿Estas seguro que deseas eliminar el Empleado?"):
        print(EmpleadoDTO().delEmpleado(emp.getId()))
    else:
        print("Operación Cancelada.")


def mostrarEmpleados() -> None:
    titulo("Listado de Empleados.")
    listar(EmpleadoDTO().findAllEmpleados(), "No hay Empleados Registrados.")


def buscarEmpleado() -> None:
    titulo("Buscar Empleado.")
    emp = seleccionarEmpleado()
    if emp is not None:
        print(emp)


# ------------------------------------------------------------------ proyectos
def registrarProyecto() -> None:
    titulo("Agregar Proyecto.")
    nombre = validaTexto("Nombre del proyecto", 3, 80)
    descripcion = validaTexto("Descripción", 3, 200)
    fecha = validaFecha("Fecha de inicio")
    print(ProyectoDTO().addProyecto(nombre, descripcion, fecha))


def modificarProyecto() -> None:
    titulo("Modificar Proyecto.")
    proy = seleccionarProyecto()
    if proy is None:
        return
    nombre = validaTexto("Nombre del proyecto", 3, 80, actual=proy.getNombre())
    descripcion = validaTexto("Descripción", 3, 200, actual=proy.getDescripcion())
    fecha = validaFecha("Fecha de inicio", actual=proy.getFechaInicio())
    print(ProyectoDTO().updateProyecto(proy.getId(), nombre, descripcion, fecha))


def eliminarProyecto() -> None:
    titulo("Eliminar Proyecto.")
    proy = seleccionarProyecto()
    if proy is None:
        return
    if validaConfirmacion("¿Estas seguro que deseas eliminar el Proyecto?"):
        print(ProyectoDTO().delProyecto(proy.getId()))
    else:
        print("Operación Cancelada.")


def listarProyectos() -> None:
    titulo("Listado de Proyectos.")
    listar(ProyectoDTO().findAllProyectos(), "No hay Proyectos Registrados.")


def buscarProyecto() -> None:
    titulo("Buscar Proyecto.")
    proy = seleccionarProyecto()
    if proy is not None:
        print(proy)


# ------------------------------------------------------------------ asignaciones
def registrarAsignacion() -> None:
    titulo("Asignar Empleado a Proyecto.")
    emp = seleccionarEmpleado()
    if emp is None:
        return
    proy = seleccionarProyecto()
    if proy is None:
        return
    fecha = validaFecha("Fecha de asignación", actual=date.today())
    print(AsignacionProyectoDTO().addAsignacion(emp, proy, fecha))


def listarAsignaciones() -> None:
    titulo("Listado de Asignaciones.")
    listar(AsignacionProyectoDTO().findAllAsignaciones(), "No hay Asignaciones Registradas.")


def listarAsignacionesPorEmpleado() -> None:
    titulo("Asignaciones por Empleado.")
    emp = seleccionarEmpleado()
    if emp is not None:
        listar(AsignacionProyectoDTO().findAsignacionesPorEmpleado(emp), "El empleado no tiene asignaciones.")


def listarAsignacionesPorProyecto() -> None:
    titulo("Asignaciones por Proyecto.")
    proy = seleccionarProyecto()
    if proy is not None:
        listar(AsignacionProyectoDTO().findAsignacionesPorProyecto(proy), "El proyecto no tiene asignaciones.")


# ------------------------------------------------------------------ registro de horas
def registrarHoras(emp=None) -> None:
    titulo("Registrar Horas Trabajadas.")
    if emp is None:
        emp = seleccionarEmpleado()
    if emp is None:
        return
    proy = seleccionarProyecto()
    if proy is None:
        return
    if not any(a.getProyecto() is proy for a in emp.getAsignaciones()):
        return print("El empleado no está asignado a ese proyecto, primero debe asignarlo.")
    fecha = validaFecha("Fecha del registro", actual=date.today(), permitirFutura=False)
    horas = validaInt("Horas trabajadas (1 a 24)", 1, 24)
    descripcion = validaTexto("Descripción de la tarea", 3, 200)
    print(RegistroTiempoDTO().addRegistro(emp, proy, fecha, horas, descripcion))


def listarRegistros() -> None:
    titulo("Listado de Registros de Tiempo.")
    listar(RegistroTiempoDTO().findAllRegistros(), "No hay Registros de Tiempo.")


def listarRegistrosPorEmpleado() -> None:
    titulo("Registros de Tiempo por Empleado.")
    emp = seleccionarEmpleado()
    if emp is not None:
        listar(RegistroTiempoDTO().findRegistrosPorEmpleado(emp), "El empleado no tiene registros.")
        print(f"Total de horas: {sum(r.getHorasTrabajadas() for r in emp.getRegistros())}")


def listarRegistrosPorProyecto() -> None:
    titulo("Registros de Tiempo por Proyecto.")
    proy = seleccionarProyecto()
    if proy is not None:
        listar(RegistroTiempoDTO().findRegistrosPorProyecto(proy), "El proyecto no tiene registros.")
        print(f"Total de horas: {sum(r.getHorasTrabajadas() for r in proy.getRegistros())}")


# ------------------------------------------------------------------ usuarios
def registrarUsuario() -> None:
    titulo("Registrar Usuario.")
    emp = seleccionarEmpleado("Id del empleado al que corresponde el usuario")
    if emp is None:
        return
    nombre = validaNombreUsuario()
    clave = validaClaveNueva()
    print("Rol: 1. ADMINISTRADOR | 2. GERENTE_RRHH (Gerente de Recursos Humanos) | 3. EMPLEADO")
    rol = permisos.ROLES[validaInt("Seleccione el rol", 1, 3) - 1]
    print(UsuarioDTO().addUsuario(nombre, clave, rol, emp.getId()))


# ------------------------------------------------------------------ menús
# Menú genérico: la última opción siempre es salir/volver. Cualquier excepción o atajo de consola
# (Ctrl+C, Ctrl+Z...) se captura aquí, así el usuario no puede cerrar el programa por accidente.
def ejecutarMenu(nombre: str, opciones: list, textoSalida: str = "Volver al Menu Principal") -> None:
    while True:
        try:
            print("\n=================================")
            print(f"===== {nombre} =====")
            print("=================================\n")
            for i, (texto, _) in enumerate(opciones, start=1):
                print(f"{i}. {texto}")
            print(f"{len(opciones) + 1}. {textoSalida}")
            print("\n(En cualquier ingreso de datos escriba 'cancelar' para volver a este menú)")
            opc = validaOpc(len(opciones) + 1)
            if opc == len(opciones) + 1:
                break
            opciones[opc - 1][1]()
        except OperacionCancelada:
            print("\n-Operación cancelada-")
        except KeyboardInterrupt:
            print("\n" + MSG_ATAJO)
        except EOFError:
            if not sys.stdin.isatty():
                raise
            print("\n" + MSG_ATAJO)
        except Exception:
            log.exception("Error inesperado en el menú '%s'", nombre)     # el detalle va al log, no a la pantalla
            print("-Ocurrió un error inesperado, intente nuevamente-")


def menuDepartamentos() -> None:
    ejecutarMenu("CRUD Departamentos", [
        ("Agregar Departamento", registrarDepto),
        ("Modificar Departamento", modificarDepto),
        ("Eliminar Departamento", eliminarDepto),
        ("Mostrar todos los Departamentos", mostrarDeptos),
        ("Buscar Departamento", buscarDepto),
        ("Agregar Empleado a un Departamento", agregarEmpleadoDepto),
        ("Reasignar Empleado a otro Departamento", reasignarEmpleadoDepto)])


def menuEmpleados() -> None:
    ejecutarMenu("CRUD Empleados", [
        ("Agregar Empleado", registrarEmpleado),
        ("Modificar Empleado", modificarEmpleado),
        ("Eliminar Empleado", eliminarEmpleado),
        ("Mostrar todos los Empleados", mostrarEmpleados),
        ("Buscar Empleado", buscarEmpleado)])


def menuProyectos() -> None:
    ejecutarMenu("CRUD Proyectos", [
        ("Agregar Proyecto", registrarProyecto),
        ("Modificar Proyecto", modificarProyecto),
        ("Eliminar Proyecto", eliminarProyecto),
        ("Mostrar todos los Proyectos", listarProyectos),
        ("Buscar Proyecto", buscarProyecto)])


def menuAsignaciones() -> None:
    ejecutarMenu("Asignaciones a Proyectos", [
        ("Asignar Empleado a Proyecto", registrarAsignacion),
        ("Mostrar todas las Asignaciones", listarAsignaciones),
        ("Asignaciones por Empleado", listarAsignacionesPorEmpleado),
        ("Asignaciones por Proyecto", listarAsignacionesPorProyecto)])


def menuRegistros() -> None:
    ejecutarMenu("Registro de Horas", [
        ("Registrar Horas Trabajadas", registrarHoras),
        ("Mostrar todos los Registros", listarRegistros),
        ("Registros por Empleado", listarRegistrosPorEmpleado),
        ("Registros por Proyecto", listarRegistrosPorProyecto)])


# Menú de proyectos de solo lectura (Gerente RRHH y Empleado)
def menuProyectosConsulta() -> None:
    ejecutarMenu("Proyectos (consulta)", [
        ("Mostrar todos los Proyectos", listarProyectos),
        ("Buscar Proyecto", buscarProyecto)])


# Menú del rol EMPLEADO: solo ve proyectos y trabaja con SUS propias asignaciones y horas
def menuEmpleadoPropio(usuario) -> None:
    def propio():
        return EmpleadoDTO().findEmpleado(usuario.getEmpleado().getId())

    def misAsignaciones() -> None:
        titulo("Mis Asignaciones.")
        listar(AsignacionProyectoDTO().findAsignacionesPorEmpleado(propio()), "No tiene asignaciones.")

    def misRegistros() -> None:
        titulo("Mis Registros de Tiempo.")
        emp = propio()
        listar(RegistroTiempoDTO().findRegistrosPorEmpleado(emp), "No tiene registros.")
        print(f"Total de horas: {sum(r.getHorasTrabajadas() for r in emp.getRegistros())}")

    ejecutarMenu("Mi Espacio de Trabajo", [
        ("Ver Proyectos", menuProyectosConsulta),
        ("Mis Asignaciones", misAsignaciones),
        ("Registrar mis Horas", lambda: registrarHoras(propio())),
        ("Mis Registros de Tiempo", misRegistros)], "Salir del Sistema")


# Menú principal (las opciones dependen del rol del usuario)
def inicial(usuario) -> None:
    from vista.menu_servicios import menuServicios      # import tardío: menu_servicios usa este módulo
    sesion.iniciar(usuario)            # define qué datos sensibles puede ver este usuario
    try:
        _menuPrincipal(usuario, menuServicios)
    finally:
        sesion.cerrar()


def _menuPrincipal(usuario, menuServicios) -> None:
    cargaInicial()
    emp = usuario.getEmpleado()
    print(f"\nBienvenido/a {emp.getNombre()} {emp.getApellido()} ({usuario.getRol()})")
    if permisos.esAdministrador(usuario):
        opciones = [("Departamentos", menuDepartamentos),
                    ("Empleados", menuEmpleados),
                    ("Proyectos", menuProyectos),
                    ("Asignaciones a Proyectos", menuAsignaciones),
                    ("Registro de Horas", menuRegistros),
                    ("Registrar Usuario", registrarUsuario)]
    elif permisos.esGerenteRRHH(usuario):
        opciones = [("Departamentos", menuDepartamentos),
                    ("Empleados", menuEmpleados),
                    ("Proyectos (consulta)", menuProyectosConsulta),
                    ("Asignaciones a Proyectos", menuAsignaciones),
                    ("Registro de Horas", menuRegistros),
                    ("Servicios Externos (indicadores y clima)", lambda: menuServicios(usuario))]
    else:
        menuEmpleadoPropio(usuario)
        return print("Programa Finalizado.")
    ejecutarMenu("EcoTech Solutions - Gestion de Empleados", opciones, "Salir del Sistema")
    print("Programa Finalizado.")
