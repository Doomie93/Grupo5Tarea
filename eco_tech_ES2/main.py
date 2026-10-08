"""Punto de entrada: ensambla las capas (inyección de dependencias) y lanza la consola."""
from types import SimpleNamespace

from conex.conexion import Conexion
from controlador.controlador_asignacion import ControladorAsignacion
from controlador.controlador_autenticacion import ControladorAutenticacion
from controlador.controlador_base import Sesion
from controlador.controlador_departamento import ControladorDepartamento
from controlador.controlador_empleado import ControladorEmpleado
from controlador.controlador_proyecto import ControladorProyecto
from controlador.controlador_registro import ControladorRegistro
from controlador.controlador_usuario import ControladorUsuario
from dao.dao_asignacion import DAOAsignacion
from dao.dao_departamento import DAODepartamento
from dao.dao_empleado import DAOEmpleado
from dao.dao_proyecto import DAOProyecto
from dao.dao_registro import DAORegistro
from dao.dao_usuario import DAOUsuario
from dao.excepciones import EcoTechError
from vista.menus import AplicacionConsola


def construir_contexto(conexion):
    """Crea DAOs y controladores; los tests reutilizan esta misma función."""
    sesion = Sesion()
    d_dep, d_emp, d_usr = DAODepartamento(conexion), DAOEmpleado(conexion), DAOUsuario(conexion)
    d_pro, d_asi, d_reg = DAOProyecto(conexion), DAOAsignacion(conexion), DAORegistro(conexion)
    return SimpleNamespace(
        sesion=sesion,
        auth=ControladorAutenticacion(sesion, d_usr),
        usuarios=ControladorUsuario(sesion, d_usr, d_emp),
        departamentos=ControladorDepartamento(sesion, d_dep),
        empleados=ControladorEmpleado(sesion, d_emp, d_dep),
        proyectos=ControladorProyecto(sesion, d_pro),
        asignaciones=ControladorAsignacion(sesion, d_asi, d_emp, d_pro),
        registros=ControladorRegistro(sesion, d_reg, d_asi),
    )


def main():
    try:
        conexion = Conexion()
    except EcoTechError as e:
        print(f"Error crítico: {e}")
        return 1
    try:
        AplicacionConsola(construir_contexto(conexion)).ejecutar()
    finally:
        conexion.cerrar()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
