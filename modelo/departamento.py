class Departamento():

    # Atributos de clase
    __listaDepartamentos = []

    # Constructor (las listas NO se cargan aquí, se cargan al iniciar la aplicación)
    def __init__(self, idDepto: int = 0, nombre: str = "", gerente: "Empleado" = None) -> None:
        self.__idDepto = idDepto
        self.__nombre = nombre
        self.__gerente = gerente
        self.__empleados = []

    # String de la clase
    def __str__(self) -> str:
        gerente = f"{self.__gerente.getNombre()} {self.__gerente.getApellido()}" if self.__gerente is not None else "Sin gerente"
        return f"Id: {self.__idDepto} | Departamento: {self.__nombre} | Gerente: {gerente} | Empleados: {len(self.__empleados)}"

    # Getters
    def getId(self) -> int:
        return self.__idDepto
    def getNombre(self) -> str:
        return self.__nombre
    def getGerente(self) -> "Empleado":
        return self.__gerente
    def getEmpleados(self) -> list:
        return self.__empleados
    def getListaDepartamentos(self) -> list:
        return self.__listaDepartamentos

    # Setters
    def setId(self, idDepto: int) -> None:
        self.__idDepto = idDepto
    def setNombre(self, nombre: str) -> None:
        self.__nombre = nombre
    def setGerente(self, gerente: "Empleado") -> None:
        self.__gerente = gerente
    def setEmpleados(self, empleados: list) -> None:
        self.__empleados = empleados

    # Carga lista de clase desde BD
    def setListaDepartamentos(self, listDB: list) -> None:
        self.__listaDepartamentos.clear()
        self.__listaDepartamentos.extend(listDB)

    # Limpia lista de clase
    def clearLista(self) -> None:
        self.__listaDepartamentos.clear()
