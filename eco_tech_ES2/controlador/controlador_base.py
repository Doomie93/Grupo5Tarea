"""Sesión y control de acceso por rol (RBAC) compartidos por los controladores."""
from dao.excepciones import PermisoError


class Sesion:
    def __init__(self):
        self._usuario = None

    @property
    def usuario(self):
        return self._usuario

    @property
    def activa(self):
        return self._usuario is not None

    def iniciar(self, usuario):
        self._usuario = usuario

    def cerrar(self):
        self._usuario = None


class ControladorBase:
    def __init__(self, sesion):
        self._sesion = sesion

    def _exigir(self, *roles):
        """Verifica que haya sesión y que el rol esté permitido. Devuelve el usuario."""
        u = self._sesion.usuario
        if u is None:
            raise PermisoError("Debe iniciar sesión.")
        if roles and u.rol not in roles:
            raise PermisoError(f"Su rol ({u.rol}) no permite esta operación.")
        return u
