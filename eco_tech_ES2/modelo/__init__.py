"""Validadores de dominio reutilizados por todas las entidades."""
import re
from datetime import date, datetime

from dao.excepciones import ValidacionError

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_RUT_RE = re.compile(r"^(\d{7,8})-([\dkK])$")


def texto_requerido(valor, campo, minimo=2, maximo=100):
    valor = (valor or "").strip() if isinstance(valor, str) or valor is None else str(valor).strip()
    if len(valor) < minimo:
        raise ValidacionError(f"{campo} debe tener al menos {minimo} caracteres.")
    if len(valor) > maximo:
        raise ValidacionError(f"{campo} no puede superar los {maximo} caracteres.")
    return valor


def texto_opcional(valor, campo, maximo=500):
    valor = (valor or "").strip()
    if len(valor) > maximo:
        raise ValidacionError(f"{campo} no puede superar los {maximo} caracteres.")
    return valor


def _digito_verificador(cuerpo):
    suma = sum(int(d) * f for d, f in zip(reversed(cuerpo), [2, 3, 4, 5, 6, 7] * 2))
    r = 11 - suma % 11
    return "0" if r == 11 else "K" if r == 10 else str(r)


def validar_rut(valor):
    """Valida formato 12345678-5 y dígito verificador (módulo 11)."""
    valor = (valor or "").strip().replace(".", "")
    m = _RUT_RE.match(valor)
    if not m:
        raise ValidacionError("RUT inválido. Formato esperado: 12345678-5")
    cuerpo, dv = m.group(1), m.group(2).upper()
    if _digito_verificador(cuerpo) != dv:
        raise ValidacionError("RUT inválido: el dígito verificador no coincide.")
    return f"{cuerpo}-{dv}"


def validar_email(valor):
    valor = (valor or "").strip().lower()
    if not _EMAIL_RE.match(valor) or len(valor) > 120:
        raise ValidacionError("Correo electrónico inválido.")
    return valor


def numero(valor, campo, minimo=None, maximo=None, estricto_minimo=False):
    try:
        n = float(str(valor).replace(",", ".")) if isinstance(valor, str) else float(valor)
    except (TypeError, ValueError):
        raise ValidacionError(f"{campo} debe ser un número.")
    if minimo is not None and (n <= minimo if estricto_minimo else n < minimo):
        raise ValidacionError(f"{campo} debe ser {'mayor que' if estricto_minimo else 'al menos'} {minimo:g}.")
    if maximo is not None and n > maximo:
        raise ValidacionError(f"{campo} no puede superar {maximo:g}.")
    return n


def parsear_fecha(valor, campo="Fecha", opcional=False):
    if valor in (None, ""):
        if opcional:
            return None
        raise ValidacionError(f"{campo} es obligatoria.")
    if isinstance(valor, datetime):
        return valor.date()
    if isinstance(valor, date):
        return valor
    try:
        return datetime.strptime(str(valor).strip(), "%Y-%m-%d").date()
    except ValueError:
        raise ValidacionError(f"{campo} inválida. Use el formato AAAA-MM-DD.")
