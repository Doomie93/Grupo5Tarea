import hashlib
import hmac
import os

ITERACIONES = 150000


# Genera "pbkdf2$iteraciones$sal$hash" (la clave nunca se guarda en texto plano)
def encriptarClave(clave: str) -> str:
    sal = os.urandom(16)
    h = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), sal, ITERACIONES)
    return f"pbkdf2${ITERACIONES}${sal.hex()}${h.hex()}"


# Compara la clave ingresada con la almacenada (comparación en tiempo constante).
# Acepta dos formatos: "pbkdf2$..." (usuarios creados desde la aplicación) y SHA-256 en hexadecimal
# (usuario inicial creado en phpMyAdmin con SHA2('clave', 256)).
def verificarClave(clave: str, almacenada: str) -> bool:
    try:
        if almacenada.startswith("pbkdf2$"):
            _, iteraciones, sal, hashGuardado = almacenada.split("$")
            calculado = hashlib.pbkdf2_hmac("sha256", clave.encode("utf-8"), bytes.fromhex(sal), int(iteraciones))
            return hmac.compare_digest(calculado.hex(), hashGuardado)
        sha = hashlib.sha256(clave.encode("utf-8")).hexdigest()
        return hmac.compare_digest(sha, almacenada.strip().lower())
    except (ValueError, AttributeError, TypeError):
        return False
