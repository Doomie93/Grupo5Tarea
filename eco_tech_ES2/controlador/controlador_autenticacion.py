import time

from dao.excepciones import AutenticacionError, NoEncontradoError, ValidacionError
from modelo.usuario import ADMIN, Usuario, validar_password

from .controlador_base import ControladorBase


class ControladorAutenticacion(ControladorBase):
    MAX_INTENTOS = 3
    BLOQUEO_SEG = 60

    def __init__(self, sesion, dao_usuario):
        super().__init__(sesion)
        self._dao = dao_usuario
        self._fallos = {}  # username -> (intentos, instante_del_ultimo_fallo)

    def hay_usuarios(self):
        return self._dao.contar() > 0

    def registrar_primer_admin(self, username, password):
        if self.hay_usuarios():
            raise ValidacionError("Ya existe un administrador; el registro inicial está cerrado.")
        return self._dao.crear(Usuario.nuevo(username, password, ADMIN))

    def iniciar_sesion(self, username, password):
        clave = (username or "").strip().lower()
        intentos, ultimo = self._fallos.get(clave, (0, 0.0))
        if intentos >= self.MAX_INTENTOS:
            restante = self.BLOQUEO_SEG - (time.monotonic() - ultimo)
            if restante > 0:
                raise AutenticacionError(f"Cuenta bloqueada temporalmente. Reintente en {int(restante) + 1} s.")
            intentos = 0
        try:
            usuario = self._dao.obtener_por_username(clave)
            ok = usuario.autenticar(password or "")
        except NoEncontradoError:
            ok = False
        if not ok:
            self._fallos[clave] = (intentos + 1, time.monotonic())
            # Mensaje genérico: no revela si el usuario existe
            raise AutenticacionError("Usuario o contraseña incorrectos.")
        self._fallos.pop(clave, None)
        self._sesion.iniciar(usuario)
        return usuario

    def cerrar_sesion(self):
        self._sesion.cerrar()

    def cambiar_mi_password(self, actual, nueva):
        u = self._exigir()
        if not u.autenticar(actual):
            raise AutenticacionError("La contraseña actual es incorrecta.")
        validar_password(nueva)
        u.cambiar_password(nueva)
        self._dao.actualizar(u)
