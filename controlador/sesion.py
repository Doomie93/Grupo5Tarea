from controlador import permisos

# Usuario con la sesión iniciada. Si no hay sesión, no se puede ver ningún dato sensible (falla cerrado).
_usuario = None


def iniciar(usuario) -> None:
    global _usuario
    _usuario = usuario


def cerrar() -> None:
    global _usuario
    _usuario = None


def actual():
    return _usuario


def puedeVerDatosSensibles() -> bool:
    return permisos.puedeVerDatosSensibles(_usuario)
