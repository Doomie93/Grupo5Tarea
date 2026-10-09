from modelo.empleado import Empleado
from modelo.proyecto import Proyecto


class RegistroTiempo():

    # Atributos de clase
    __listaRegistros = []

    # Constructor
    def __init__(self, fecha=None, horasTrabajadas: int = 0, descripcionTarea: str = "",
                 empleado: Empleado = None, proyecto: Proyecto = None) -> None:
        self.__fecha = fecha
        self.__horasTrabajadas = horasTrabajadas
        self.__descripcionTarea = descripcionTarea
        self.__empleado = empleado
        self.__proyecto = proyecto

    # String de la clase
    def __str__(self) -> str:
        fecha = self.__fecha.strftime("%d-%m-%Y") if self.__fecha is not None else "-"
        emp = f"{self.__empleado.getNombre()} {self.__empleado.getApellido()}" if self.__empleado is not None else "-"
        proy = self.__proyecto.getNombre() if self.__proyecto is not None else "-"
        return (f"Fecha: {fecha} | Empleado: {emp} | Proyecto: {proy} | "
                f"Horas: {self.__horasTrabajadas} | Tarea: {self.__descripcionTarea}")

    # Getters
    def getFecha(self):
        return self.__fecha
    def getHorasTrabajadas(self) -> int:
        return self.__horasTrabajadas
    def getDescripcionTarea(self) -> str:
        return self.__descripcionTarea
    def getEmpleado(self) -> Empleado:
        return self.__empleado
    def getProyecto(self) -> Proyecto:
        return self.__proyecto
    def getListaRegistros(self) -> list:
        return self.__listaRegistros

    # Setters
    def setFecha(self, fecha) -> None:
        self.__fecha = fecha
    def setHorasTrabajadas(self, horas: int) -> None:
        self.__horasTrabajadas = horas
    def setDescripcionTarea(self, descripcion: str) -> None:
        self.__descripcionTarea = descripcion
    def setEmpleado(self, empleado: Empleado) -> None:
        self.__empleado = empleado
    def setProyecto(self, proyecto: Proyecto) -> None:
        self.__proyecto = proyecto

    # Carga lista de clase desde BD
    def setListaRegistros(self, listDB: list) -> None:
        self.__listaRegistros.clear()
        self.__listaRegistros.extend(listDB)

    # Limpia lista de clase
    def clearLista(self) -> None:
        self.__listaRegistros.clear()
