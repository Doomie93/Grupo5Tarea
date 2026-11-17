import logging
from vista.entrada import bloquearAtajos, pedir, esFinDeEntrada, MSG_ATAJO, OperacionCancelada
from vista.menus import probarConexion, validarLogin, inicial

MAX_INTENTOS = 3
log = logging.getLogger("ecotech")


# Los detalles técnicos de los errores se guardan en este archivo; en pantalla solo se muestran mensajes genéricos
def configurarLog() -> None:
    logging.basicConfig(filename="ecotech_errores.log", level=logging.WARNING, encoding="utf-8",
                        format="%(asctime)s %(levelname)s %(name)s: %(message)s")


# Registra el detalle en el log y retorna un mensaje que no expone información interna
def _errorGenerico(ex: BaseException) -> str:
    log.error("Error inesperado: %r", ex)
    return "-Ocurrió un error inesperado, intente nuevamente-"


# Verifica la conexión con la BD ya existente; permite reintentar si MySQL aún no está activo
def conectarBD() -> bool:
    while True:
        try:
            if probarConexion():
                return True
            pedir("Presione ENTER para reintentar o escriba 'cancelar' para salir: ")
        except OperacionCancelada:
            return False
        except (Exception, KeyboardInterrupt) as ex:
            if esFinDeEntrada(ex):
                return False
            print(MSG_ATAJO if isinstance(ex, KeyboardInterrupt) else _errorGenerico(ex))


# Login con 3 intentos; Ctrl+C / errores no cierran el programa ni cuentan como intento.
# Escribir "cancelar" (o dejar la contraseña vacía) cierra el programa.
def login():
    intentos = 0
    while intentos < MAX_INTENTOS:
        try:
            usuario = validarLogin()
            if usuario is not None:
                return usuario
            intentos += 1
            print(f"-Usuario o Contraseña incorrecta- (intento {intentos} de {MAX_INTENTOS})")
        except OperacionCancelada:
            print("-Inicio de sesión cancelado-")
            return None
        except (Exception, KeyboardInterrupt) as ex:
            if esFinDeEntrada(ex):
                return None
            print(MSG_ATAJO if isinstance(ex, KeyboardInterrupt) else _errorGenerico(ex))
            print("-Intente nuevamente-")
    print("-Acceso bloqueado por demasiados intentos-")
    return None


def main() -> None:
    configurarLog()
    bloquearAtajos()
    print("\n=== EcoTech Solutions ===\n")
    if not conectarBD():
        return
    usuario = login()
    if usuario is None:
        return
    print("-Acceso Permitido-")
    while True:
        try:
            inicial(usuario)
            break
        except (Exception, KeyboardInterrupt) as ex:
            if esFinDeEntrada(ex):
                break
            print(MSG_ATAJO if isinstance(ex, KeyboardInterrupt) else _errorGenerico(ex))


if __name__ == "__main__":
    main()
