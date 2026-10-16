import re
from datetime import date, datetime
from vista.entrada import pedir, pedirClave


# Validacion para el ingreso de valores tipo INT (con rango opcional y valor actual opcional)
def validaInt(txt: str, minimo: int = None, maximo: int = None, actual: int = None) -> int:
    while True:
        sufijo = f" [{actual}] (ENTER para mantener)" if actual is not None else ""
        valor = pedir(f"{txt}{sufijo}: ").strip()
        if valor == "" and actual is not None:
            return actual
        try:
            numero = int(valor)
        except ValueError:
            print("Error de ingreso, solo puedes ingresar números enteros.")
            continue
        if minimo is not None and numero < minimo:
            print(f"El valor debe ser mayor o igual a {minimo}.")
        elif maximo is not None and numero > maximo:
            print(f"El valor debe ser menor o igual a {maximo}.")
        else:
            return numero


# Validacion de textos por largo mínimo y máximo (coincide con el tamaño de las columnas de la BD)
def validaTexto(txt: str, minimo: int, maximo: int, actual: str = None) -> str:
    while True:
        sufijo = f" [{actual}] (ENTER para mantener)" if actual is not None else ""
        valor = pedir(f"{txt}{sufijo}: ").strip()
        if valor == "" and actual is not None:
            return actual
        if minimo <= len(valor) <= maximo:
            return valor
        print(f"Campo incorrecto, debe tener entre {minimo} y {maximo} caracteres.")


def validaCorreo(actual: str = None) -> str:
    while True:
        sufijo = f" [{actual}] (ENTER para mantener)" if actual is not None else ""
        valor = pedir(f"Correo (xxxx@xxxx.xx){sufijo}: ").strip()
        if valor == "" and actual is not None:
            return actual
        if len(valor) <= 100 and re.fullmatch(r"[\w.+-]+@[\w-]+(\.[\w-]+)+", valor):
            return valor
        print("Correo inválido, use el formato nombre@dominio.cl")


def validaTelefono(actual: str = None) -> str:
    while True:
        sufijo = f" [{actual}] (ENTER para mantener)" if actual is not None else ""
        valor = pedir(f"Teléfono (8 a 14 dígitos, puede iniciar con +){sufijo}: ").strip()
        if valor == "" and actual is not None:
            return actual
        if re.fullmatch(r"\+?\d{8,14}", valor):
            return valor
        print("Teléfono inválido, ingrese solo dígitos (8 a 14).")


# Fecha en formato DD-MM-AAAA; si hay valor actual, ENTER lo acepta
def validaFecha(txt: str, actual: date = None, permitirFutura: bool = True) -> date:
    while True:
        sufijo = f" [{actual.strftime('%d-%m-%Y')}] (ENTER para aceptar)" if actual is not None else " (DD-MM-AAAA)"
        valor = pedir(f"{txt}{sufijo}: ").strip()
        if valor == "" and actual is not None:
            return actual
        try:
            fecha = datetime.strptime(valor, "%d-%m-%Y").date()
        except ValueError:
            print("Fecha inválida, use el formato DD-MM-AAAA (ej: 15-03-2024).")
            continue
        if not permitirFutura and fecha > date.today():
            print("La fecha no puede ser posterior a hoy.")
            continue
        return fecha


def validaNombreUsuario() -> str:
    while True:
        valor = pedir("Nombre de usuario (4 a 30 caracteres: letras, números, . o _): ").strip()
        if re.fullmatch(r"[A-Za-z0-9_.]{4,30}", valor):
            return valor
        print("Nombre de usuario inválido.")


# Clave nueva: oculta con "*", mínimo 8 caracteres con letras y números, y debe repetirse igual
def validaClaveNueva() -> str:
    while True:
        clave = pedirClave("Ingrese contraseña (mín. 8 caracteres, letras y números; ENTER vacío para cancelar): ")
        if len(clave) < 8 or len(clave) > 50 or not re.search(r"[A-Za-z]", clave) or not re.search(r"\d", clave):
            print("Contraseña débil: use entre 8 y 50 caracteres, con al menos una letra y un número.")
            continue
        if clave != pedirClave("Repita la contraseña (ENTER vacío para cancelar): "):
            print("Las contraseñas no coinciden.")
            continue
        return clave


# Confirmación S/N
def validaConfirmacion(msg: str) -> bool:
    while True:
        resp = pedir(f"{msg} (S/N): ").strip().upper()
        if resp in ("S", "Y"):
            return True
        if resp == "N":
            return False
        print("Opción inválida, ingrese S o N.")


# Validador de opciones para los menús
def validaOpc(num: int) -> int:
    return validaInt("Ingrese una opción", 1, num)
