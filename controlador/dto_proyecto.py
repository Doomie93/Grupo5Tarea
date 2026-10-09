from controlador.base_dto import BaseDTO
from modelo.proyecto import Proyecto
from dao.dao_proyecto import ProyectoDAO


class ProyectoDTO(BaseDTO):

    # Pasa datos desde la BD a la lista de clase
    def cargarDatos(self) -> None:
        filas = ProyectoDAO().cargarDatos() or []
        lista = [Proyecto(f["IDPROYECTO"], f["NOMBRE"], f["DESCRIPCION"], f["FECHAINICIO"]) for f in filas]
        Proyecto().setListaProyectos(lista)

    def findAllProyectos(self) -> list:
        return ProyectoDAO().listarProyectos()

    def findProyecto(self, idProyecto: int) -> Proyecto:
        return ProyectoDAO().buscarProyecto(idProyecto)

    def addProyecto(self, nombre: str, descripcion: str, fechaInicio) -> str:
        res = ProyectoDAO().registrarProyecto(Proyecto(0, nombre, descripcion, fechaInicio))
        return self.mensaje(res, "Proyecto agregado satisfactoriamente.")

    def updateProyecto(self, idProyecto: int, nombre: str, descripcion: str, fechaInicio) -> str:
        res = ProyectoDAO().modificarProyecto(Proyecto(idProyecto, nombre, descripcion, fechaInicio))
        return self.mensaje(res, "Proyecto modificado satisfactoriamente.")

    def delProyecto(self, idProyecto: int) -> str:
        res = ProyectoDAO().eliminarProyecto(idProyecto)
        return self.mensaje(res, "Proyecto eliminado satisfactoriamente.")
