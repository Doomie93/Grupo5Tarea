from vista.entrada import bloquearAtajos, pedir, esFinDeEntrada, MSG_ATAJO
from vista.menus import probarConexion, validarLogin, inicial

MAX_INTENTOS = 3


# Verifica la conexión con la BD ya existente; permite reintentar si MySQL aún no está activo
def conectarBD() -> bool:
    while True:
        try:
            if probarConexion():
                return True
            if pedir("Presione ENTER para reintentar o escriba 'salir': ").strip().lower() == "salir":
                return False
        except (Exception, KeyboardInterrupt) as ex:
            if esFinDeEntrada(ex):
                return False
            print(MSG_ATAJO if isinstance(ex, KeyboardInterrupt) else f"-Error inesperado: {ex}-")


# Login con 3 intentos; Ctrl+C / errores no cierran el programa ni cuentan como intento
def login():
    intentos = 0
    while intentos < MAX_INTENTOS:
        try:
            usuario = validarLogin()
            if usuario is not None:
                return usuario
            intentos += 1
            print(f"-Usuario o Contraseña incorrecta- (intento {intentos} de {MAX_INTENTOS})")
        except (Exception, KeyboardInterrupt) as ex:
            if esFinDeEntrada(ex):
                return None
            print(MSG_ATAJO if isinstance(ex, KeyboardInterrupt) else f"-Error inesperado: {ex}-")
            print("-Intente nuevamente-")
    print("-Acceso bloqueado por demasiados intentos-")
    return None


def main() -> None:
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
            print(MSG_ATAJO if isinstance(ex, KeyboardInterrupt) else f"-Error inesperado: {ex}-")


if __name__ == "__main__":
    main()
