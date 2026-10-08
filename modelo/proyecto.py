from datetime import date

from dao.excepciones import ValidacionError

from . import numero, parsear_fecha, texto_opcional, texto_requerido

ESTADOS = ("PLANIFICADO", "EN_CURSO", "FINALIZADO", "CANCELADO")


class Proyecto:
    def __init__(self, nombre, fecha_inicio, descripcion="", fecha_fin=None,
                 estado="PLANIFICADO", presupuesto=0, id=None):
        self.id = id
        self.nombre = nombre
        self.descripcion = descripcion
        self.__fecha_fin = None
        self.fecha_inicio = fecha_inicio
        self.fecha_fin = fecha_fin
        self.estado = estado
        self.presupuesto = presupuesto

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, v):
        self.__nombre = texto_requerido(v, "El nombre del proyecto", 3, 80)

    @property
    def descripcion(self):
        return self.__descripcion

    @descripcion.setter
    def descripcion(self, v):
        self.__descripcion = texto_opcional(v, "La descripción", 500)

    @property
    def fecha_inicio(self):
        return self.__fecha_inicio

    @fecha_inicio.setter
    def fecha_inicio(self, v):
        f = parsear_fecha(v, "La fecha de inicio")
        if self.__fecha_fin and self.__fecha_fin < f:
            raise ValidacionError("La fecha de término no puede ser anterior al inicio.")
        self.__fecha_inicio = f

    @property
    def fecha_fin(self):
        return self.__fecha_fin

    @fecha_fin.setter
    def fecha_fin(self, v):
        f = parsear_fecha(v, "La fecha de término", opcional=True)
        if f and f < self.__fecha_inicio:
            raise ValidacionError("La fecha de término no puede ser anterior al inicio.")
        self.__fecha_fin = f

    @property
    def estado(self):
        return self.__estado

    @estado.setter
    def estado(self, v):
        v = (v or "").upper()
        if v not in ESTADOS:
            raise ValidacionError(f"Estado inválido. Opciones: {', '.join(ESTADOS)}")
        self.__estado = v

    @property
    def presupuesto(self):
        return self.__presupuesto

    @presupuesto.setter
    def presupuesto(self, v):
        self.__presupuesto = numero(v, "El presupuesto", minimo=0, maximo=1e12)

    def acepta_asignaciones(self):
        return self.estado in ("PLANIFICADO", "EN_CURSO")

    def dias_restantes(self):
        return None if self.fecha_fin is None else (self.fecha_fin - date.today()).days

    def __str__(self):
        return f"[{self.id}] {self.nombre} ({self.estado})"
