from dao.base_dao import BaseDAO
from dao.seguridad import encriptarClave, verificarClave
from modelo.usuario import Usuario
from modelo.empleado import Empleado


class UsuarioDAO(BaseDAO):

    # Registra un usuario (la clave se guarda encriptada)
    def registrarUsuario(self, usuario: Usuario) -> int:
        return self._ejecutar("insert into USUARIO (NOMBREUSUARIO, CLAVE, ROL, IDEMPLEADO) values (%s, %s, %s, %s)",
                              (usuario.getNombreUsuario(), encriptarClave(usuario.getClave()),
                               usuario.getRol(), usuario.getEmpleado().getId()))

    # Retorna el Usuario si las credenciales son correctas, de lo contrario None
    def validarAcceso(self, nombreUsuario: str, clave: str) -> Usuario:
        sql = ("select U.IDUSUARIO, U.NOMBREUSUARIO, U.CLAVE, U.ROL, E.IDEMPLEADO, E.NOMBRE, E.APELLIDO "
               "from USUARIO U join EMPLEADO E on E.IDEMPLEADO = U.IDEMPLEADO where U.NOMBREUSUARIO = %s")
        filas = self._consultar(sql, (nombreUsuario,))
        if not filas:
            return None
        fila = filas[0]
        if not verificarClave(clave, fila["CLAVE"]):
            return None
        empleado = Empleado(idEmpleado=fila["IDEMPLEADO"], nombre=fila["NOMBRE"], apellido=fila["APELLIDO"])
        return Usuario(fila["IDUSUARIO"], fila["NOMBREUSUARIO"], "", fila["ROL"], empleado)
