from dao.base_dao import BaseDAO
from modelo.registro_tiempo import RegistroTiempo
from modelo.empleado import Empleado
from modelo.proyecto import Proyecto


class RegistroTiempoDAO(BaseDAO):

    # Trae todas las filas de REGISTROTIEMPO (el DTO las convierte en objetos)
    def cargarDatos(self) -> list:
        return self._consultar("select FECHA, HORASTRABAJADAS, DESCRIPCIONTAREA, IDEMPLEADO, IDPROYECTO "
                               "from REGISTROTIEMPO order by IDREGISTRO")

    # Agrega el registro a la BD, a la lista de clase y a las listas del empleado y del proyecto
    def registrarHorasTrabajadas(self, empleado: Empleado, proyecto: Proyecto, fecha, horas: int, descripcion: str) -> int:
        res = self._ejecutar("insert into REGISTROTIEMPO (FECHA, HORASTRABAJADAS, DESCRIPCIONTAREA, IDEMPLEADO, IDPROYECTO) "
                             "values (%s, %s, %s, %s, %s)",
                             (fecha, horas, descripcion, empleado.getId(), proyecto.getId()))
        if res > 0:
            registro = RegistroTiempo(fecha, horas, descripcion, empleado, proyecto)
            RegistroTiempo().getListaRegistros().append(registro)
            empleado.getRegistros().append(registro)
            proyecto.getRegistros().append(registro)
        return res

    def listarRegistrosTiempo(self) -> list:
        return RegistroTiempo().getListaRegistros()

    def listarRegistrosTiempoPorEmpleado(self, empleado: Empleado) -> list:
        return empleado.getRegistros()

    def listarRegistrosTiempoPorProyecto(self, proyecto: Proyecto) -> list:
        return proyecto.getRegistros()
