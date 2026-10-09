from modelo.empleado import Empleado
from modelo.proyecto import Proyecto


class AsignacionProyecto():

    # Atributos de clase
    __listaAsignaciones = []

    # Constructor
    def __init__(self, idAsignacion: int = 0, fechaAsignacion=None, empleado: Empleado = None,
                 proyecto: Proyecto = None) -> None:
        self.__idAsignacion = idAsignacion
        self.__fechaAsignacion = fechaAsignacion
        self.__empleado = empleado
        self.__proyecto = proyecto

    # String de la clase
    def __str__(self) -> str:
        fecha = self.__fechaAsignacion.strftime("%d-%m-%Y") if self.__fechaAsignacion is not None else "-"
        emp = f"{self.__empleado.getNombre()} {self.__empleado.getApellido()}" if self.__empleado is not None else "-"
        proy = self.__proyecto.getNombre() if self.__proyecto is not None else "-"
        return f"Id: {self.__idAsignacion} | Fecha: {fecha} | Empleado: {emp} | Proyecto: {proy}"

    # Getters
    def getId(self) -> int:
        return self.__idAsignacion
    def getFechaAsignacion(self):
        return self.__fechaAsignacion
    def getEmpleado(self) -> Empleado:
        return self.__empleado
    def getProyecto(self) -> Proyecto:
        return self.__proyecto
    def getListaAsignaciones(self) -> list:
        return self.__listaAsignaciones

    # Setters
    def setId(self, idAsignacion: int) -> None:
        self.__idAsignacion = idAsignacion
    def setFechaAsignacion(self, fechaAsignacion) -> None:
        self.__fechaAsignacion = fechaAsignacion
    def setEmpleado(self, empleado: Empleado) -> None:
        self.__empleado = empleado
    def setProyecto(self, proyecto: Proyecto) -> None:
        self.__proyecto = proyecto

    # Carga lista de clase desde BD
    def setListaAsignaciones(self, listDB: list) -> None:
        self.__listaAsignaciones.clear()
        self.__listaAsignaciones.extend(listDB)

    # Limpia lista de clase
    def clearLista(self) -> None:
        self.__listaAsignaciones.clear()
