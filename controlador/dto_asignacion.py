from controlador.base_dto import BaseDTO
from modelo.asignacion_proyecto import AsignacionProyecto
from modelo.empleado import Empleado
from modelo.proyecto import Proyecto
from dao.dao_asignacion import AsignacionProyectoDAO
from dao.dao_empleado import EmpleadoDAO
from dao.dao_proyecto import ProyectoDAO


class AsignacionProyectoDTO(BaseDTO):

    # Pasa datos desde la BD a la lista de clase y a las listas del empleado y del proyecto
    def cargarDatos(self) -> None:
        filas = AsignacionProyectoDAO().cargarDatos() or []
        lista = []
        for f in filas:
            emp = EmpleadoDAO().buscarEmpleado(f["IDEMPLEADO"])
            proy = ProyectoDAO().buscarProyecto(f["IDPROYECTO"])
            asig = AsignacionProyecto(f["IDASIGNACION"], f["FECHAASIGNACION"], emp, proy)
            if emp is not None:
                emp.getAsignaciones().append(asig)
            if proy is not None:
                proy.getAsignaciones().append(asig)
            lista.append(asig)
        AsignacionProyecto().setListaAsignaciones(lista)

    def findAllAsignaciones(self) -> list:
        return AsignacionProyectoDAO().listarAsignaciones()

    def findAsignacionesPorEmpleado(self, empleado: Empleado) -> list:
        return AsignacionProyectoDAO().listarAsignacionesPorEmpleado(empleado)

    def findAsignacionesPorProyecto(self, proyecto: Proyecto) -> list:
        return AsignacionProyectoDAO().listarAsignacionesPorProyecto(proyecto)

    def addAsignacion(self, empleado: Empleado, proyecto: Proyecto, fecha) -> str:
        res = AsignacionProyectoDAO().registrarAsignacion(AsignacionProyecto(0, fecha, empleado, proyecto))
        return self.mensaje(res, "Asignación registrada satisfactoriamente.")
