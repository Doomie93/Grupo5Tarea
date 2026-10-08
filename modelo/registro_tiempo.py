from datetime import date

from dao.excepciones import ValidacionError

from . import numero, parsear_fecha, texto_opcional


class RegistroTiempo:
    """Horas trabajadas por un empleado en una asignación, en una fecha."""

    def __init__(self, id_asignacion, fecha, horas, descripcion="", id=None):
        self.id = id
        self.id_asignacion = id_asignacion
        self.fecha = fecha
        self.horas = horas
        self.descripcion = descripcion

    @property
    def fecha(self):
        return self.__fecha

    @fecha.setter
    def fecha(self, v):
        f = parsear_fecha(v, "La fecha del registro")
        if f > date.today():
            raise ValidacionError("No se pueden registrar horas en una fecha futura.")
        self.__fecha = f

    @property
    def horas(self):
        return self.__horas

    @horas.setter
    def horas(self, v):
        self.__horas = numero(v, "Las horas", minimo=0, maximo=24, estricto_minimo=True)

    @property
    def descripcion(self):
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, v):
        self.__descripcion = texto_opcional(v, "La descripción", 300)

    def __str__(self):
        return f"[{self.id}] {self.fecha} · {self.horas:g} h"
