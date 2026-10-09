class Proyecto():

    # Atributos de clase
    __listaProyectos = []

    # Constructor (las listas NO se cargan aquí, se cargan al iniciar la aplicación)
    def __init__(self, idProyecto: int = 0, nombre: str = "", descripcion: str = "", fechaInicio=None) -> None:
        self.__idProyecto = idProyecto
        self.__nombre = nombre
        self.__descripcion = descripcion
        self.__fechaInicio = fechaInicio
        self.__asignaciones = []
        self.__registros = []

    # String de la clase
    def __str__(self) -> str:
        fecha = self.__fechaInicio.strftime("%d-%m-%Y") if self.__fechaInicio is not None else "-"
        return f"Id: {self.__idProyecto} | Proyecto: {self.__nombre} | Inicio: {fecha} | Descripción: {self.__descripcion}"

    # Getters
    def getId(self) -> int:
        return self.__idProyecto
    def getNombre(self) -> str:
        return self.__nombre
    def getDescripcion(self) -> str:
        return self.__descripcion
    def getFechaInicio(self):
        return self.__fechaInicio
    def getAsignaciones(self) -> list:
        return self.__asignaciones
    def getRegistros(self) -> list:
        return self.__registros
    def getListaProyectos(self) -> list:
        return self.__listaProyectos

    # Setters
    def setId(self, idProyecto: int) -> None:
        self.__idProyecto = idProyecto
    def setNombre(self, nombre: str) -> None:
        self.__nombre = nombre
    def setDescripcion(self, descripcion: str) -> None:
        self.__descripcion = descripcion
    def setFechaInicio(self, fechaInicio) -> None:
        self.__fechaInicio = fechaInicio
    def setAsignaciones(self, asignaciones: list) -> None:
        self.__asignaciones = asignaciones
    def setRegistros(self, registros: list) -> None:
        self.__registros = registros

    # Carga lista de clase desde BD
    def setListaProyectos(self, listDB: list) -> None:
        self.__listaProyectos.clear()
        self.__listaProyectos.extend(listDB)

    # Limpia lista de clase
    def clearLista(self) -> None:
        self.__listaProyectos.clear()
