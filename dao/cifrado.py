import hashlib
import hmac
import logging
import os
from cryptography.fernet import Fernet, InvalidToken

log = logging.getLogger("ecotech.cifrado")

# Texto que ven los usuarios sin permiso en lugar del dato real
MASCARA = "[ENCRIPTADO]"
ILEGIBLE = "[ILEGIBLE]"

VARIABLE_CLAVE = "ECOTECH_CLAVE_CIFRADO"
ARCHIVO_CLAVE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "clave_cifrado.key")
_fernet = None
_clave = None


# La clave se lee de la variable de entorno ECOTECH_CLAVE_CIFRADO o del archivo clave_cifrado.key (ignorado por git).
# Si no existe ninguna, se genera una nueva. Sin esta clave los datos cifrados NO se pueden recuperar.
def _obtenerClave() -> bytes:
    global _clave
    if _clave is None:
        valor = os.environ.get(VARIABLE_CLAVE)
        if valor:
            _clave = valor.strip().encode()
        elif os.path.exists(ARCHIVO_CLAVE):
            with open(ARCHIVO_CLAVE, "rb") as f:
                _clave = f.read().strip()
        else:
            _clave = Fernet.generate_key()
            fd = os.open(ARCHIVO_CLAVE, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            with os.fdopen(fd, "wb") as f:
                f.write(_clave)
            print("Se generó la clave de cifrado en 'clave_cifrado.key'. Respáldela: sin ella los datos cifrados no se recuperan.")
    return _clave


def _cifrador() -> Fernet:
    global _fernet
    if _fernet is None:
        try:
            _fernet = Fernet(_obtenerClave())
        except (ValueError, TypeError):
            raise RuntimeError("La clave de cifrado es inválida (debe ser una clave Fernet de 44 caracteres).")
    return _fernet


# Cifrado simétrico autenticado (Fernet: AES-128-CBC + HMAC-SHA256). Retorna texto listo para guardar en la BD.
def cifrar(texto: str) -> str:
    return _cifrador().encrypt(str(texto).encode("utf-8")).decode("ascii")


# Retorna el texto original o None si el token no es válido (clave distinta o dato alterado)
def descifrar(token: str):
    try:
        return _cifrador().decrypt(token.encode("ascii")).decode("utf-8")
    except (InvalidToken, ValueError, AttributeError):
        log.error("No se pudo descifrar un dato (clave incorrecta o dato alterado)")
        return None


# Los tokens Fernet siempre comienzan con "gAAAA"; sirve para detectar datos aún sin cifrar
def estaCifrado(valor) -> bool:
    return isinstance(valor, str) and valor.startswith("gAAAA")


# Huella del correo (HMAC-SHA256 con la clave) para poder exigir correos únicos sin guardarlo en claro
def huellaCorreo(correo: str) -> str:
    return hmac.new(b"correo:" + _obtenerClave(), correo.strip().lower().encode("utf-8"), hashlib.sha256).hexdigest()
