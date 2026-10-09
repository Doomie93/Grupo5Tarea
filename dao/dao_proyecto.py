from dao.base_dao import BaseDAO
from modelo.proyecto import Proyecto


class ProyectoDAO(BaseDAO):

    # Trae todas las filas de PROYECTO (el DTO las convierte en objetos)
    def cargarDatos(self) -> list:
        return self._consultar("select IDPROYECTO, NOMBRE, DESCRIPCION, FECHAINICIO from PROYECTO order by IDPROYECTO")

    # Agrega un proyecto a la BD y a la lista de clase
    def registrarProyecto(self, proyecto: Proyecto) -> int:
        res = self._ejecutar("insert into PROYECTO (NOMBRE, DESCRIPCION, FECHAINICIO) values (%s, %s, %s)",
                             (proyecto.getNombre(), proyecto.getDescripcion(), proyecto.getFechaInicio()))
        if res > 0:
            proyecto.setId(self.getUltimoId())
            Proyecto().getListaProyectos().append(proyecto)
        return res

    # Retorna la lista de clase
    def listarProyectos(self) -> list:
        return Proyecto().getListaProyectos()

    # Busca un proyecto en la lista de clase
    def buscarProyecto(self, idProyecto: int) -> Proyecto:
        for proy in Proyecto().getListaProyectos():
            if proy.getId() == idProyecto:
                return proy
        return None

    # Modifica en la BD y actualiza el objeto de la lista
    def modificarProyecto(self, proyecto: Proyecto) -> int:
        res = self._ejecutar("update PROYECTO set NOMBRE = %s, DESCRIPCION = %s, FECHAINICIO = %s where IDPROYECTO = %s",
                             (proyecto.getNombre(), proyecto.getDescripcion(), proyecto.getFechaInicio(), proyecto.getId()))
        if res > 0:
            actual = self.buscarProyecto(proyecto.getId())
            if actual is not None:
                actual.setNombre(proyecto.getNombre())
                actual.setDescripcion(proyecto.getDescripcion())
                actual.setFechaInicio(proyecto.getFechaInicio())
        return res

    # Elimina de la BD y de la lista de clase
    def eliminarProyecto(self, idProyecto: int) -> int:
        res = self._ejecutar("delete from PROYECTO where IDPROYECTO = %s", (idProyecto,))
        if res > 0:
            lista = Proyecto().getListaProyectos()
            lista[:] = [p for p in lista if p.getId() != idProyecto]
        return res
