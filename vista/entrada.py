import getpass
import os
import signal
import sys

MSG_ATAJO = "-Acción no permitida: para salir use la opción 'Salir' o 'Volver' del menú-"


# Indica si la entrada estándar se cerró (ejecución sin consola interactiva)
def esFinDeEntrada(ex: BaseException) -> bool:
    return isinstance(ex, EOFError) and not sys.stdin.isatty()


# Ignora las señales que cerrarían o suspenderían el programa (Ctrl+Z, Ctrl+\ y Ctrl+Pausa)
def bloquearAtajos() -> None:
    for nombre in ("SIGTSTP", "SIGQUIT", "SIGBREAK"):
        senal = getattr(signal, nombre, None)
        if senal is not None:
            try:
                signal.signal(senal, signal.SIG_IGN)
            except (ValueError, OSError):
                pass


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


# Lee una clave mostrando "*" por cada carácter escrito
def pedirClave(prompt: str = "Ingrese contraseña: ") -> str:
    if not sys.stdin.isatty():
        # Sin consola real (ej. IDLE o entrada redirigida) no se puede controlar el eco
        return getpass.getpass(prompt)
    sys.stdout.write(prompt)
    sys.stdout.flush()
    if os.name == "nt":
        return _leerClaveWindows()
    return _leerClaveUnix()


def _leerClaveWindows() -> str:
    import msvcrt
    chars = []
    while True:
        try:
            ch = msvcrt.getwch()
        except KeyboardInterrupt:
            continue
        if ch in ("\r", "\n"):
            sys.stdout.write("\n")
            sys.stdout.flush()
            return "".join(chars)
        if ch in ("\x00", "\xe0"):          # teclas especiales (flechas, F1...): se descarta la segunda parte
            msvcrt.getwch()
        elif ch == "\x08":                  # retroceso
            if chars:
                chars.pop()
                sys.stdout.write("\b \b")
                sys.stdout.flush()
        elif ch in ("\x03", "\x1a", "\x04", "\x1b"):   # Ctrl+C, Ctrl+Z, Ctrl+D, ESC: se ignoran
            continue
        elif ch.isprintable():
            chars.append(ch)
            sys.stdout.write("*")
            sys.stdout.flush()


def _leerClaveUnix() -> str:
    import select
    import termios
    import tty
    fd = sys.stdin.fileno()
    anterior = termios.tcgetattr(fd)
    chars = []
    try:
        tty.setraw(fd)      # modo "raw": Ctrl+C y Ctrl+Z llegan como caracteres, no como señales
        while True:
            b = os.read(fd, 1)
            if not b:
                continue
            n = b[0]
            if n in (13, 10):                       # ENTER
                sys.stdout.write("\r\n")
                sys.stdout.flush()
                return "".join(chars)
            if n in (127, 8):                       # retroceso
                if chars:
                    chars.pop()
                    sys.stdout.write("\b \b")
                    sys.stdout.flush()
            elif n == 27:                           # ESC / flechas: se descarta la secuencia completa
                while select.select([fd], [], [], 0.02)[0]:
                    os.read(fd, 1)
            elif n < 32:                            # Ctrl+C, Ctrl+Z, Ctrl+D, etc.: se ignoran
                continue
            else:
                extra = 1 if 0xC0 <= n < 0xE0 else 2 if 0xE0 <= n < 0xF0 else 3 if n >= 0xF0 else 0
                for _ in range(extra):
                    b += os.read(fd, 1)
                chars.append(b.decode("utf-8", errors="ignore"))
                sys.stdout.write("*")
                sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, anterior)
