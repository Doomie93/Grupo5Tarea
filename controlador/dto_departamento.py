from controlador.base_dto import BaseDTO
from modelo.departamento import Departamento
from dao.dao_departamento import DepartamentoDAO
from dao.dao_empleado import EmpleadoDAO


class DepartamentoDTO(BaseDTO):

    def __init__(self) -> None:
        self.__filas = []

    # Pasa datos desde la BD a la lista de clase (el gerente se vincula después de cargar los empleados)
    def cargarDatos(self) -> None:
        self.__filas = DepartamentoDAO().cargarDatos() or []
        lista = []
        for fila in self.__filas:
            lista.append(Departamento(fila["IDDEPARTAMENTO"], fila["NOMBRE"]))
        Departamento().setListaDepartamentos(lista)

    # Enlaza cada departamento con su gerente (objeto Empleado)
    def vincularGerentes(self) -> None:
        for fila in self.__filas:
            if fila["IDGERENTE"] is not None:
                depto = DepartamentoDAO().buscarDepto(fila["IDDEPARTAMENTO"])
                depto.setGerente(EmpleadoDAO().buscarEmpleado(fila["IDGERENTE"]))

    def findAllDeptos(self) -> list:
        return DepartamentoDAO().mostrarDeptos()

    def findDepto(self, idDepto: int) -> Departamento:
        return DepartamentoDAO().buscarDepto(idDepto)

    def addDepto(self, nombre: str, idGerente: int = None) -> str:
        gerente = EmpleadoDAO().buscarEmpleado(idGerente) if idGerente is not None else None
        res = DepartamentoDAO().registrarDepto(Departamento(nombre=nombre, gerente=gerente))
        return self.mensaje(res, "Departamento agregado satisfactoriamente.")

    def updateDepto(self, idDepto: int, nombre: str, idGerente: int = None) -> str:
        gerente = EmpleadoDAO().buscarEmpleado(idGerente) if idGerente is not None else None
        res = DepartamentoDAO().modificarDepto(Departamento(idDepto, nombre, gerente))
        return self.mensaje(res, "Departamento modificado satisfactoriamente.")

    def delDepto(self, idDepto: int) -> str:
        res = DepartamentoDAO().eliminarDepto(idDepto)
        return self.mensaje(res, "Departamento eliminado satisfactoriamente.")

    def addEmpleadoDepto(self, idEmpleado: int, idDepto: int) -> str:
        res = DepartamentoDAO().agregarEmpleadoDepto(EmpleadoDAO().buscarEmpleado(idEmpleado),
                                                     DepartamentoDAO().buscarDepto(idDepto))
        return self.mensaje(res, "Empleado agregado al departamento satisfactoriamente.")

    def reasignarEmpleadoDepto(self, idEmpleado: int, idDepto: int) -> str:
        res = DepartamentoDAO().reasignarEmpleadoDepto(EmpleadoDAO().buscarEmpleado(idEmpleado),
                                                       DepartamentoDAO().buscarDepto(idDepto))
        return self.mensaje(res, "Empleado reasignado satisfactoriamente.")
