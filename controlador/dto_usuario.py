from controlador.base_dto import BaseDTO
from modelo.usuario import Usuario
from dao.dao_usuario import UsuarioDAO
from dao.dao_empleado import EmpleadoDAO


class UsuarioDTO(BaseDTO):

    def validarAcceso(self, nombreUsuario: str, clave: str) -> Usuario:
        return UsuarioDAO().validarAcceso(nombreUsuario, clave)

    def addUsuario(self, nombreUsuario: str, clave: str, rol: str, idEmpleado: int) -> str:
        empleado = EmpleadoDAO().buscarEmpleado(idEmpleado)
        res = UsuarioDAO().registrarUsuario(Usuario(0, nombreUsuario, clave, rol, empleado))
        return self.mensaje(res, "Usuario registrado satisfactoriamente.")
