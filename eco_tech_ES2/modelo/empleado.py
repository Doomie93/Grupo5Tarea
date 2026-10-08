"""Jerarquía de empleados: clase abstracta + 3 especializaciones (herencia/polimorfismo)."""
from abc import ABC, abstractmethod
from datetime import date

from dao.excepciones import ValidacionError

from . import numero, parsear_fecha, texto_requerido, validar_email, validar_rut


class Empleado(ABC):
    TIPO = "BASE"

    def __init__(self, rut, nombre, email, salario_base, fecha_ingreso=None,
                 id_departamento=None, activo=True, id=None):
        self.id = id
        self.rut = rut
        self.nombre = nombre
        self.email = email
        self.salario_base = salario_base
        self.fecha_ingreso = fecha_ingreso or date.today()
        self.id_departamento = id_departamento
        self.activo = bool(activo)

    # --- Encapsulamiento: atributos privados + propiedades que validan ---
    @property
    def rut(self):
        return self.__rut

    @rut.setter
    def rut(self, v):
        self.__rut = validar_rut(v)

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, v):
        self.__nombre = texto_requerido(v, "El nombre", 2, 80)

    @property
    def email(self):
        return self.__email

    @email.setter
    def email(self, v):
        self.__email = validar_email(v)

    @property
    def salario_base(self):
        return self.__salario_base

    @salario_base.setter
    def salario_base(self, v):
        self.__salario_base = numero(v, "El salario", minimo=0, maximo=1e9, estricto_minimo=True)

    @property
    def fecha_ingreso(self):
        return self.__fecha_ingreso

    @fecha_ingreso.setter
    def fecha_ingreso(self, v):
        f = parsear_fecha(v, "La fecha de ingreso")
        if f > date.today():
            raise ValidacionError("La fecha de ingreso no puede ser futura.")
        self.__fecha_ingreso = f

    # --- Comportamiento ---
    @abstractmethod
    def calcular_salario(self):
        """Remuneración líquida estimada; cada subclase la define (polimorfismo)."""

    def antiguedad_anios(self):
        hoy = date.today()
        f = self.fecha_ingreso
        return hoy.year - f.year - ((hoy.month, hoy.day) < (f.month, f.day))

    def __str__(self):
        return f"[{self.id}] {self.nombre} ({self.TIPO})"


class EmpleadoPlanta(Empleado):
    TIPO = "PLANTA"

    def calcular_salario(self):
        return self.salario_base


class EmpleadoHonorarios(Empleado):
    TIPO = "HONORARIOS"
    RETENCION = 0.1375

    def calcular_salario(self):
        return self.salario_base * (1 - self.RETENCION)


class Gerente(Empleado):
    TIPO = "GERENTE"
    BONO = 0.20

    def calcular_salario(self):
        return self.salario_base * (1 + self.BONO)


TIPOS_EMPLEADO = {c.TIPO: c for c in (EmpleadoPlanta, EmpleadoHonorarios, Gerente)}


def crear_empleado(tipo, **datos):
    """Fábrica: construye la subclase correcta según el tipo."""
    try:
        clase = TIPOS_EMPLEADO[str(tipo).upper()]
    except KeyError:
        raise ValidacionError(f"Tipo de empleado inválido. Opciones: {', '.join(TIPOS_EMPLEADO)}")
    return clase(**datos)
