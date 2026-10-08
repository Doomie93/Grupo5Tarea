"""Jerarquía de excepciones de la aplicación.

Todas heredan de EcoTechError, de modo que la capa de vista puede capturar
los errores *esperados* con un único `except EcoTechError`.
"""


class EcoTechError(Exception):
    """Error base de la aplicación."""


class ValidacionError(EcoTechError):
    """Dato de entrada o regla de negocio inválida."""


class BaseDatosError(EcoTechError):
    """Falla de conexión u operación en la base de datos."""


class DuplicadoError(BaseDatosError):
    """Violación de una restricción UNIQUE (RUT, correo, usuario...)."""


class NoEncontradoError(EcoTechError):
    """El registro solicitado no existe."""


class AutenticacionError(EcoTechError):
    """Credenciales inválidas o cuenta bloqueada."""


class PermisoError(EcoTechError):
    """El rol del usuario no permite la operación."""
