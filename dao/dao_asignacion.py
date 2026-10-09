from dao.base_dao import BaseDAO
from modelo.asignacion_proyecto import AsignacionProyecto
from modelo.empleado import Empleado
from modelo.proyecto import Proyecto


class AsignacionProyectoDAO(BaseDAO):

    # Trae todas las filas de ASIGNACIONPROYECTO (el DTO las convierte en objetos)
    def cargarDatos(self) -> list:
        return self._consultar("select IDASIGNACION, FECHAASIGNACION, IDEMPLEADO, IDPROYECTO "
                               "from ASIGNACIONPROYECTO order by IDASIGNACION")

    # Agrega la asignación a la BD, a la lista de clase y a las listas del empleado y del proyecto
    def registrarAsignacion(self, asignacion: AsignacionProyecto) -> int:
        res = self._ejecutar("insert into ASIGNACIONPROYECTO (FECHAASIGNACION, IDEMPLEADO, IDPROYECTO) values (%s, %s, %s)",
                             (asignacion.getFechaAsignacion(), asignacion.getEmpleado().getId(),
                              asignacion.getProyecto().getId()))
        if res > 0:
            asignacion.setId(self.getUltimoId())
            AsignacionProyecto().getListaAsignaciones().append(asignacion)
            asignacion.getEmpleado().getAsignaciones().append(asignacion)
            asignacion.getProyecto().getAsignaciones().append(asignacion)
        return res

    def listarAsignaciones(self) -> list:
        return AsignacionProyecto().getListaAsignaciones()

    def listarAsignacionesPorEmpleado(self, empleado: Empleado) -> list:
        return empleado.getAsignaciones()

    def listarAsignacionesPorProyecto(self, proyecto: Proyecto) -> list:
        return proyecto.getAsignaciones()
