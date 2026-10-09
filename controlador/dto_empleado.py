from controlador.base_dto import BaseDTO
from modelo.empleado import Empleado
from dao.dao_empleado import EmpleadoDAO
from dao.dao_departamento import DepartamentoDAO


class EmpleadoDTO(BaseDTO):

    # Pasa datos desde la BD a la lista de clase y a la lista de empleados de cada departamento
    def cargarDatos(self) -> None:
        filas = EmpleadoDAO().cargarDatos() or []
        lista = []
        for f in filas:
            depto = DepartamentoDAO().buscarDepto(f["IDDEPARTAMENTO"]) if f["IDDEPARTAMENTO"] is not None else None
            emp = Empleado(f["IDEMPLEADO"], f["NOMBRE"], f["APELLIDO"], f["CORREO"], f["FECHACONTRATO"],
                           f["SALARIO"], f["DIRECCION"], f["TELEFONO"], depto)
            if depto is not None:
                depto.getEmpleados().append(emp)
            lista.append(emp)
        Empleado().setListaEmpleados(lista)

    def findAllEmpleados(self) -> list:
        return EmpleadoDAO().mostrarEmpleados()

    def findEmpleado(self, idEmpleado: int) -> Empleado:
        return EmpleadoDAO().buscarEmpleado(idEmpleado)

    def addEmpleado(self, nombre: str, apellido: str, correo: str, fechaContrato, salario: int,
                    direccion: str, telefono: str, idDepto: int = None) -> str:
        depto = DepartamentoDAO().buscarDepto(idDepto) if idDepto is not None else None
        res = EmpleadoDAO().registrarEmpleado(Empleado(0, nombre, apellido, correo, fechaContrato, salario,
                                                       direccion, telefono, depto))
        return self.mensaje(res, "Empleado agregado satisfactoriamente.")

    def updateEmpleado(self, idEmpleado: int, nombre: str, apellido: str, correo: str, fechaContrato,
                       salario: int, direccion: str, telefono: str) -> str:
        res = EmpleadoDAO().modificarEmpleado(Empleado(idEmpleado, nombre, apellido, correo, fechaContrato,
                                                       salario, direccion, telefono))
        return self.mensaje(res, "Empleado modificado satisfactoriamente.")

    def delEmpleado(self, idEmpleado: int) -> str:
        res = EmpleadoDAO().eliminarEmpleado(idEmpleado)
        return self.mensaje(res, "Empleado eliminado satisfactoriamente.")
