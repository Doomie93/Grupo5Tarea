from modelo.departamento import Departamento


class Empleado():

    # Atributos de clase
    __listaEmpleados = []

    # Constructor (las listas NO se cargan aquí, se cargan al iniciar la aplicación)
    def __init__(self, idEmpleado: int = 0, nombre: str = "", apellido: str = "", correo: str = "",
                 fechaContrato=None, salario: int = 0, direccion: str = "", telefono: str = "",
                 departamento: Departamento = None) -> None:
        self.__idEmpleado = idEmpleado
        self.__nombre = nombre
        self.__apellido = apellido
        self.__correo = correo
        self.__fechaContrato = fechaContrato
        self.__salario = salario
        self.__direccion = direccion
        self.__telefono = telefono
        self.__departamento = departamento
        self.__asignaciones = []
        self.__registros = []

    # String de la clase
    def __str__(self) -> str:
        fecha = self.__fechaContrato.strftime("%d-%m-%Y") if self.__fechaContrato is not None else "-"
        depto = self.__departamento.getNombre() if self.__departamento is not None else "Sin departamento"
        salario = f"${self.__salario:,}".replace(",", ".")
        return (f"Id: {self.__idEmpleado} | {self.__nombre} {self.__apellido} | Correo: {self.__correo} | "
                f"Contrato: {fecha} | Salario: {salario} | Tel: {self.__telefono} | "
                f"Dirección: {self.__direccion} | Departamento: {depto}")

    # Getters
    def getId(self) -> int:
        return self.__idEmpleado
    def getNombre(self) -> str:
        return self.__nombre
    def getApellido(self) -> str:
        return self.__apellido
    def getCorreo(self) -> str:
        return self.__correo
    def getFechaContrato(self):
        return self.__fechaContrato
    def getSalario(self) -> int:
        return self.__salario
    def getDireccion(self) -> str:
        return self.__direccion
    def getTelefono(self) -> str:
        return self.__telefono
    def getDepartamento(self) -> Departamento:
        return self.__departamento
    def getAsignaciones(self) -> list:
        return self.__asignaciones
    def getRegistros(self) -> list:
        return self.__registros
    def getListaEmpleados(self) -> list:
        return self.__listaEmpleados

    # Setters
    def setId(self, idEmpleado: int) -> None:
        self.__idEmpleado = idEmpleado
    def setNombre(self, nombre: str) -> None:
        self.__nombre = nombre
    def setApellido(self, apellido: str) -> None:
        self.__apellido = apellido
    def setCorreo(self, correo: str) -> None:
        self.__correo = correo
    def setFechaContrato(self, fechaContrato) -> None:
        self.__fechaContrato = fechaContrato
    def setSalario(self, salario: int) -> None:
        self.__salario = salario
    def setDireccion(self, direccion: str) -> None:
        self.__direccion = direccion
    def setTelefono(self, telefono: str) -> None:
        self.__telefono = telefono
    def setDepartamento(self, departamento: Departamento) -> None:
        self.__departamento = departamento
    def setAsignaciones(self, asignaciones: list) -> None:
        self.__asignaciones = asignaciones
    def setRegistros(self, registros: list) -> None:
        self.__registros = registros

    # Carga lista de clase desde BD
    def setListaEmpleados(self, listDB: list) -> None:
        self.__listaEmpleados.clear()
        self.__listaEmpleados.extend(listDB)

    # Limpia lista de clase
    def clearLista(self) -> None:
        self.__listaEmpleados.clear()
