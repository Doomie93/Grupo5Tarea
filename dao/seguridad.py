import hashlib
import hmac
import os

ITERACIONES = 150000


# Genera "pbkdf2$iteraciones$sal$hash" (la clave nunca se guarda en texto plano)
def encriptarClave(clave: str) -> str:
    sal = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, ITERACIONES)
    return f"pbkdf2${ITERACIONES}${sal.hex()}${h.hex()}"


# Compara la clave ingresada con la almacenada (comparación en tiempo constante)
def verificarClave(clave: str, almacenada: str) -> bool:
    try:
        _, iteraciones, sal, hashGuardado = almacenada.split("$")
        calculado = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), bytes.fromhex(sal), int(iteraciones))
        return hmac.compare_digest(calculado.hex(), hashGuardado)
    except (ValueError, AttributeError):
        return False
