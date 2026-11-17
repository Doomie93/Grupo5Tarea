class Indicador():

    # Constructor
    def __init__(self, idIndicador: int = 0, idUsuario: int = 0, autor: str = "", codigo: str = "",
                 fecha=None, valor: float = 0.0, nombreUsuario: str = "") -> None:
        self.__idIndicador = idIndicador
        self.__idUsuario = idUsuario
        self.__autor = autor
        self.__codigo = codigo
        self.__fecha = fecha
        self.__valor = valor
        self.__nombreUsuario = nombreUsuario

    # String de la clase (formato chileno: 1.234,56)
    def __str__(self) -> str:
        fecha = self.__fecha.strftime("%d-%m-%Y") if self.__fecha is not None else "-"
        valor = f"{self.__valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        quien = f" | Consultó: {self.__nombreUsuario}" if self.__nombreUsuario else ""
        return f"{fecha} | {self.__codigo.upper():<5} | {valor:>14} | Fuente: {self.__autor}{quien}"

    # Getters
    def getId(self) -> int:
        return self.__idIndicador
    def getIdUsuario(self) -> int:
        return self.__idUsuario
    def getAutor(self) -> str:
        return self.__autor
    def getCodigo(self) -> str:
        return self.__codigo
    def getFecha(self):
        return self.__fecha
    def getValor(self) -> float:
        return self.__valor
    def getNombreUsuario(self) -> str:
        return self.__nombreUsuario
