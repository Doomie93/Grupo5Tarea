from modelo.empleado import Empleado


class Usuario():

    # Constructor
    def __init__(self, idUsuario: int = 0, nombreUsuario: str = "", clave: str = "", rol: str = "",
                 empleado: Empleado = None) -> None:
        self.__idUsuario = idUsuario
        self.__nombreUsuario = nombreUsuario
        self.__clave = clave
        self.__rol = rol
        self.__empleado = empleado

    # String de la clase (nunca incluye la clave)
    def __str__(self) -> str:
        emp = f"{self.__empleado.getNombre()} {self.__empleado.getApellido()}" if self.__empleado is not None else "-"
        return f"Usuario: {self.__nombreUsuario} | Rol: {self.__rol} | Empleado: {emp}"

    # Getters
    def getId(self) -> int:
        return self.__idUsuario
    def getNombreUsuario(self) -> str:
        return self.__nombreUsuario
    def getClave(self) -> str:
        return self.__clave
    def getRol(self) -> str:
        return self.__rol
    def getEmpleado(self) -> Empleado:
        return self.__empleado

    # Setters
    def setId(self, idUsuario: int) -> None:
        self.__idUsuario = idUsuario
    def setNombreUsuario(self, nombreUsuario: str) -> None:
        self.__nombreUsuario = nombreUsuario
    def setClave(self, clave: str) -> None:
        self.__clave = clave
    def setRol(self, rol: str) -> None:
        self.__rol = rol
    def setEmpleado(self, empleado: Empleado) -> None:
        self.__empleado = empleado
