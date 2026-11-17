from controlador.base_dto import BaseDTO
from modelo.empleado import Empleado
from dao.dao_empleado import EmpleadoDAO
from dao.dao_departamento import DepartamentoDAO


class EmpleadoDTO(BaseDTO):

    # Cifra los datos sensibles que hayan quedado en claro en la BD (se llama al iniciar el sistema)
    def cifrarPendientes(self) -> int:
        return EmpleadoDAO().cifrarPendientes()

    # Pasa datos desde la BD a la lista de clase y a la lista de empleados de cada departamento
    def cargarDatos(self) -> None:
        filas = EmpleadoDAO().cargarDatos() or []
        lista = []
        for f in filas:
            depto = DepartamentoDAO().buscarDepto(f["IDDEPARTAMENTO"]) if f["IDDEPARTAMENTO"] is not None else None
            emp = Empleado(f["IDEMPLEADO"], f["NOMBRE"], f["APELLIDO"], "", f["FECHACONTRATO"], None, "",
                           f["TELEFONO"], depto)
            emp.setDatosCifrados(f["CORREO"], f["CORREOHASH"], f["SALARIO"], f["DIRECCION"])     # ya vienen cifrados
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
        actual = EmpleadoDAO().buscarEmpleado(idEmpleado)
        if actual is None:
            return "-Empleado no encontrado-"
        # Se parte de los datos cifrados actuales; los setters ignoran "[ENCRIPTADO]" (campo no modificado)
        nuevo = Empleado(idEmpleado, nombre, apellido, "", fechaContrato, None, "", telefono)
        nuevo.copiarDatosCifrados(actual)
        nuevo.setCorreo(correo)
        nuevo.setSalario(salario)
        nuevo.setDireccion(direccion)
        res = EmpleadoDAO().modificarEmpleado(nuevo)
        return self.mensaje(res, "Empleado modificado satisfactoriamente.")

    def delEmpleado(self, idEmpleado: int) -> str:
        res = EmpleadoDAO().eliminarEmpleado(idEmpleado)
        return self.mensaje(res, "Empleado eliminado satisfactoriamente.")
