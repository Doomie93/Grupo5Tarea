import getpass
import os
import signal
import sys

if os.name == "nt":
    import msvcrt          # Windows
else:
    import termios         # Linux / macOS
    import tty

MSG_ATAJO = "-Acción no permitida: para salir use la opción 'Salir' o 'Volver' del menú-"

# Teclas especiales que reconoce la lectura de la contraseña
ENTER = ("\r", "\n")              # Windows entrega \r y Unix puede entregar \r o \n
RETROCESO = ("\b", "\x7f")        # tecla de borrar: Windows entrega \b y Unix \x7f
BORRAR_ASTERISCO = "\b \b"        # retrocede el cursor, tapa el * con un espacio y retrocede de nuevo


# Indica si la entrada estándar se cerró (ejecución sin consola interactiva)
def esFinDeEntrada(ex: BaseException) -> bool:
    return isinstance(ex, EOFError) and not sys.stdin.isatty()


# Ignora los atajos que cerrarían o suspenderían el programa, según el sistema operativo
def bloquearAtajos() -> None:
    if os.name == "nt":
        signal.signal(signal.SIGBREAK, signal.SIG_IGN)      # Ctrl+Pausa
    else:
        signal.signal(signal.SIGTSTP, signal.SIG_IGN)       # Ctrl+Z
        signal.signal(signal.SIGQUIT, signal.SIG_IGN)       # Ctrl+\


# input() que no deja salir con Ctrl+C / Ctrl+Z / Ctrl+D: avisa y vuelve a preguntar
def pedir(prompt: str = "") -> str:
    while True:
        try:
            return input(prompt)
        except KeyboardInterrupt:
            print("\n" + MSG_ATAJO)
        except EOFError:
            if not sys.stdin.isatty():
                raise
            print("\n" + MSG_ATAJO)


# Pide la contraseña y la retorna. Prepara la consola según el sistema operativo
# para que lo escrito no se muestre; el "*" lo dibuja _leerClave.
def pedirClave(prompt: str = "Ingrese contraseña: ") -> str:
    if not sys.stdin.isatty():
        # Sin consola real (ej. IDLE o entrada redirigida) no se puede ocultar con "*"
        return getpass.getpass(prompt)
    print(prompt, end="", flush=True)
    if os.name == "nt":
        clave = _leerClave()
    else:
        fd = sys.stdin.fileno()
        configuracionOriginal = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)      # en este modo Ctrl+C y Ctrl+Z llegan como teclas normales
            clave = _leerClave()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, configuracionOriginal)
    print()
    return clave


# Lee una tecla sin mostrarla en pantalla
def _leerTecla() -> str:
    if os.name == "nt":
        return msvcrt.getwch()
    return sys.stdin.read(1)


# Lee la contraseña tecla por tecla: la va guardando y muestra un "*" por cada carácter
def _leerClave() -> str:
    clave = ""
    while True:
        tecla = _leerTecla()
        if tecla in ENTER:
            return clave
        if tecla in RETROCESO:
            if clave != "":
                clave = clave[:-1]
                print(BORRAR_ASTERISCO, end="", flush=True)
        elif tecla.isprintable():
            clave = clave + tecla
            print("*", end="", flush=True)
        # cualquier otra tecla (Ctrl+C, Ctrl+Z, etc.) se ignora
