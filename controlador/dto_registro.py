from controlador.base_dto import BaseDTO
from modelo.registro_tiempo import RegistroTiempo
from modelo.empleado import Empleado
from modelo.proyecto import Proyecto
from dao.dao_registro import RegistroTiempoDAO
from dao.dao_empleado import EmpleadoDAO
from dao.dao_proyecto import ProyectoDAO


class RegistroTiempoDTO(BaseDTO):

    # Pasa datos desde la BD a la lista de clase y a las listas del empleado y del proyecto
    def cargarDatos(self) -> None:
        filas = RegistroTiempoDAO().cargarDatos() or []
        lista = []
        for f in filas:
            emp = EmpleadoDAO().buscarEmpleado(f["IDEMPLEADO"])
            proy = ProyectoDAO().buscarProyecto(f["IDPROYECTO"])
            reg = RegistroTiempo(f["FECHA"], f["HORASTRABAJADAS"], f["DESCRIPCIONTAREA"], emp, proy)
            if emp is not None:
                emp.getRegistros().append(reg)
            if proy is not None:
                proy.getRegistros().append(reg)
            lista.append(reg)
        RegistroTiempo().setListaRegistros(lista)

    def findAllRegistros(self) -> list:
        return RegistroTiempoDAO().listarRegistrosTiempo()

    def findRegistrosPorEmpleado(self, empleado: Empleado) -> list:
        return RegistroTiempoDAO().listarRegistrosTiempoPorEmpleado(empleado)

    def findRegistrosPorProyecto(self, proyecto: Proyecto) -> list:
        return RegistroTiempoDAO().listarRegistrosTiempoPorProyecto(proyecto)

    def addRegistro(self, empleado: Empleado, proyecto: Proyecto, fecha, horas: int, descripcion: str) -> str:
        res = RegistroTiempoDAO().registrarHorasTrabajadas(empleado, proyecto, fecha, horas, descripcion)
        return self.mensaje(res, "Horas registradas satisfactoriamente.")
