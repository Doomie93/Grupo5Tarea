from modelo.departamento import Departamento
from controlador import sesion
from dao import cifrado


class Empleado():

    # Atributos de clase
    __listaEmpleados = []

    # Constructor (las listas NO se cargan aquí, se cargan al iniciar la aplicación)
    def __init__(self, idEmpleado: int = 0, nombre: str = "", apellido: str = "", correo: str = "",
                 fechaContrato=None, salario: int = None, direccion: str = "", telefono: str = "",
                 departamento: Departamento = None) -> None:
        self.__idEmpleado = idEmpleado
        self.__nombre = nombre
        self.__apellido = apellido
        # Correo, salario, dirección y teléfono se guardan SIEMPRE cifrados (así también viajan a la BD)
        self.__correo = ""
        self.__correoHash = ""
        self.__salario = ""
        self.__direccion = ""
        self.__telefono = ""
        self.__fechaContrato = fechaContrato
        if correo:
            self.setCorreo(correo)
        if salario is not None:
            self.setSalario(salario)
        if direccion:
            self.setDireccion(direccion)
        if telefono:
            self.setTelefono(telefono)
        self.__departamento = departamento
        self.__asignaciones = []
        self.__registros = []

    # String de la clase
    def __str__(self) -> str:
        fecha = self.__fechaContrato.strftime("%d-%m-%Y") if self.__fechaContrato is not None else "-"
        depto = self.__departamento.getNombre() if self.__departamento is not None else "Sin departamento"
        sueldo = self.getSalario()
        salario = f"${sueldo:,}".replace(",", ".") if isinstance(sueldo, int) else sueldo
        return (f"Id: {self.__idEmpleado} | {self.__nombre} {self.__apellido} | Correo: {self.getCorreo()} | "
                f"Contrato: {fecha} | Salario: {salario} | Tel: {self.getTelefono()} | "
                f"Dirección: {self.getDireccion()} | Departamento: {depto}")

    # Entrega el dato descifrado solo si el usuario de la sesión tiene permiso; si no, el texto "[ENCRIPTADO]"
    def __ver(self, token: str):
        if token == "":
            return ""
        if not sesion.puedeVerDatosSensibles():
            return cifrado.MASCARA
        dato = cifrado.descifrar(token)
        return cifrado.ILEGIBLE if dato is None else dato

    # Getters
    def getId(self) -> int:
        return self.__idEmpleado
    def getNombre(self) -> str:
        return self.__nombre
    def getApellido(self) -> str:
        return self.__apellido
    def getCorreo(self) -> str:
        return self.__ver(self.__correo)
    def getFechaContrato(self):
        return self.__fechaContrato
    def getSalario(self):
        dato = self.__ver(self.__salario)
        return int(dato) if dato not in ("", cifrado.MASCARA, cifrado.ILEGIBLE) else dato
    def getDireccion(self) -> str:
        return self.__ver(self.__direccion)
    def getTelefono(self) -> str:
        return self.__ver(self.__telefono)

    # Valores cifrados tal como se guardan en la BD (nunca exponen el dato original)
    def getCorreoCifrado(self) -> str:
        return self.__correo
    def getSalarioCifrado(self) -> str:
        return self.__salario
    def getDireccionCifrada(self) -> str:
        return self.__direccion
    def getTelefonoCifrado(self) -> str:
        return self.__telefono
    def getCorreoHash(self) -> str:
        return self.__correoHash
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
    # Los setters reciben el dato en claro y lo cifran. Si llega "[ENCRIPTADO]" (quien no puede ver el dato
    # presionó ENTER para mantenerlo) se ignora y se conserva el valor actual.
    def setCorreo(self, correo: str) -> None:
        if correo == cifrado.MASCARA:
            return
        self.__correo = cifrado.cifrar(correo)
        self.__correoHash = cifrado.huellaCorreo(correo)
    def setFechaContrato(self, fechaContrato) -> None:
        self.__fechaContrato = fechaContrato
    def setSalario(self, salario: int) -> None:
        if salario == cifrado.MASCARA:
            return
        self.__salario = cifrado.cifrar(int(salario))
    def setDireccion(self, direccion: str) -> None:
        if direccion == cifrado.MASCARA:
            return
        self.__direccion = cifrado.cifrar(direccion)
    def setTelefono(self, telefono: str) -> None:
        if telefono == cifrado.MASCARA:
            return
        self.__telefono = cifrado.cifrar(telefono)

    # Carga los valores ya cifrados (desde la BD) o los copia desde otro empleado, sin pasar por el dato en claro
    def setDatosCifrados(self, correo: str, correoHash: str, salario: str, direccion: str, telefono: str) -> None:
        self.__correo = correo
        self.__correoHash = correoHash
        self.__salario = salario
        self.__direccion = direccion
        self.__telefono = telefono
    def copiarDatosCifrados(self, otro) -> None:
        self.setDatosCifrados(otro.getCorreoCifrado(), otro.getCorreoHash(), otro.getSalarioCifrado(),
                              otro.getDireccionCifrada(), otro.getTelefonoCifrado())
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
