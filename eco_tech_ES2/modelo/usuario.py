"""Usuario del sistema. Las contraseñas NUNCA se guardan en texto plano:
se almacena PBKDF2-HMAC-SHA256 con sal aleatoria."""
import hashlib
import hmac
import os
import re

from dao.excepciones import ValidacionError

from . import texto_requerido

ADMIN, GERENTE, EMPLEADO = "ADMIN", "GERENTE", "EMPLEADO"
ROLES = (ADMIN, GERENTE, EMPLEADO)
_ITER = 200_000


def validar_password(pw):
    pw = pw or ""
    if len(pw) < 8 or not re.search(r"[A-Za-z]", pw) or not re.search(r"\d", pw):
        raise ValidacionError("La contraseña debe tener al menos 8 caracteres, letras y números.")
    return pw


def hashear_password(pw):
    sal = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", pw.encode(), sal, _ITER)
    return f"pbkdf2${_ITER}${sal.hex()}${h.hex()}"


def verificar_password(pw, almacenado):
    try:
        _, it, sal, h = almacenado.split("$")
        calc = hashlib.pbkdf2_hmac("sha256", pw.encode(), bytes.fromhex(sal), int(it))
        return hmac.compare_digest(calc.hex(), h)  # comparación en tiempo constante
    except (ValueError, AttributeError):
        return False


class Usuario:
    def __init__(self, username, password_hash, rol, id_empleado=None, activo=True, id=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.rol = rol
        self.id_empleado = id_empleado
        self.activo = bool(activo)

    @classmethod
    def nuevo(cls, username, password, rol, id_empleado=None):
        """Crea un usuario validando la contraseña y guardando solo su hash."""
        return cls(username, hashear_password(validar_password(password)), rol, id_empleado)

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, v):
        v = texto_requerido(v, "El usuario", 3, 30)
        if not re.fullmatch(r"[A-Za-z0-9_.-]+", v):
            raise ValidacionError("El usuario solo admite letras, números, '.', '_' y '-'.")
        self.__username = v.lower()

    @property
    def rol(self):
        return self.__rol

    @rol.setter
    def rol(self, v):
        v = (v or "").upper()
        if v not in ROLES:
            raise ValidacionError(f"Rol inválido. Opciones: {', '.join(ROLES)}")
        self.__rol = v

    def cambiar_password(self, nueva):
        self.password_hash = hashear_password(validar_password(nueva))

    def autenticar(self, password):
        return self.activo and verificar_password(password, self.password_hash)

    def __str__(self):
        return f"[{self.id}] {self.username} ({self.rol})"
