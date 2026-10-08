from dao.excepciones import ValidacionError
from modelo.usuario import ADMIN, EMPLEADO, Usuario

from .controlador_base import ControladorBase


class ControladorUsuario(ControladorBase):
    def __init__(self, sesion, dao_usuario, dao_empleado):
        super().__init__(sesion)
        self._dao = dao_usuario
        self._dao_emp = dao_empleado

    def crear(self, username, password, rol, id_empleado=None):
        self._exigir(ADMIN)
        if id_empleado is not None:
            self._dao_emp.obtener(id_empleado)  # debe existir
        elif (rol or "").upper() == EMPLEADO:
            raise ValidacionError("Un usuario con rol EMPLEADO debe estar vinculado a un empleado.")
        return self._dao.crear(Usuario.nuevo(username, password, rol, id_empleado))

    def listar(self):
        self._exigir(ADMIN)
        return self._dao.listar()

    def cambiar_estado(self, id_usuario, activo):
        actual = self._exigir(ADMIN)
        u = self._dao.obtener(id_usuario)
        if not activo:
            if u.id == actual.id:
                raise ValidacionError("No puede desactivar su propia cuenta.")
            if u.rol == ADMIN and self._dao.contar_admins_activos() <= 1:
                raise ValidacionError("Debe quedar al menos un administrador activo.")
        u.activo = activo
        self._dao.actualizar(u)

    def eliminar(self, id_usuario):
        actual = self._exigir(ADMIN)
        u = self._dao.obtener(id_usuario)
        if u.id == actual.id:
            raise ValidacionError("No puede eliminar su propia cuenta.")
        if u.rol == ADMIN and u.activo and self._dao.contar_admins_activos() <= 1:
            raise ValidacionError("Debe quedar al menos un administrador activo.")
        self._dao.eliminar(id_usuario)
