"""Entrada de datos por consola con validación y reintento.

Cada `pedir_*` repite la pregunta hasta recibir un valor válido, así un dato
mal digitado nunca interrumpe el programa. Las reglas de dominio (RUT, correo,
fechas...) se reutilizan desde el paquete `modelo`, sin duplicarlas.
"""
import getpass

from dao.excepciones import ValidacionError
from modelo import numero, parsear_fecha


def pedir_con(mensaje, validador, defecto=None):
    """Pide un texto y lo pasa por `validador` (que lanza ValidacionError si es inválido).
    Si hay `defecto`, Enter lo conserva."""
    etiqueta = f"{mensaje} [{defecto}]: " if defecto not in (None, "") else f"{mensaje}: "
    while True:
        txt = input(etiqueta).strip()
        if not txt and defecto is not None:
            return defecto
        try:
            return validador(txt)
        except ValidacionError as e:
            print(f"   ✗ {e}")


def pedir_texto(mensaje, minimo=1, maximo=100, defecto=None):
    def v(t):
        if len(t) < minimo:
            raise ValidacionError(f"Debe tener al menos {minimo} caracteres.")
        if len(t) > maximo:
            raise ValidacionError(f"No puede superar los {maximo} caracteres.")
        return t
    return pedir_con(mensaje, v, defecto)


def pedir_texto_opcional(mensaje, defecto=""):
    return input(f"{mensaje} (Enter = {'mantener' if defecto else 'omitir'}): ").strip() or defecto


def pedir_entero(mensaje, minimo=None, maximo=None, defecto=None):
    def v(t):
        try:
            n = int(t)
        except ValueError:
            raise ValidacionError("Debe ingresar un número entero.")
        if minimo is not None and n < minimo:
            raise ValidacionError(f"Debe ser al menos {minimo}.")
        if maximo is not None and n > maximo:
            raise ValidacionError(f"No puede superar {maximo}.")
        return n
    return pedir_con(mensaje, v, defecto)


def pedir_decimal(mensaje, minimo=0, maximo=None, estricto=False, defecto=None):
    return pedir_con(mensaje, lambda t: numero(t, "El valor", minimo, maximo, estricto), defecto)


def pedir_fecha(mensaje, opcional=False, defecto=None):
    sufijo = " (AAAA-MM-DD" + (", Enter = omitir)" if opcional else ")")
    if opcional and defecto is None:
        return _fecha_opcional(mensaje + sufijo)
    return pedir_con(mensaje + sufijo, lambda t: parsear_fecha(t, "La fecha"), defecto)


def _fecha_opcional(etiqueta):
    while True:
        txt = input(f"{etiqueta}: ").strip()
        if not txt:
            return None
        try:
            return parsear_fecha(txt)
        except ValidacionError as e:
            print(f"   ✗ {e}")


def pedir_opcion(mensaje, opciones, defecto=None):
    """Elige una opción de una lista (sin distinguir mayúsculas)."""
    mapa = {o.upper(): o for o in opciones}

    def v(t):
        if t.upper() not in mapa:
            raise ValidacionError(f"Opciones válidas: {', '.join(opciones)}")
        return mapa[t.upper()]
    return pedir_con(f"{mensaje} ({'/'.join(opciones)})", v, defecto)


def confirmar(mensaje):
    return input(f"{mensaje} (s/N): ").strip().lower() in ("s", "si", "sí", "y", "yes")


def pedir_password(mensaje="Contraseña"):
    try:
        return getpass.getpass(f"{mensaje}: ")
    except (EOFError, getpass.GetPassWarning):
        return input(f"{mensaje}: ")
