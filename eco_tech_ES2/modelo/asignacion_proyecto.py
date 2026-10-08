from datetime import date

from . import numero, parsear_fecha, texto_requerido


class AsignacionProyecto:
    """Relación N:M entre Empleado y Proyecto, con rol y horas comprometidas."""

    def __init__(self, id_empleado, id_proyecto, rol_proyecto, horas_asignadas,
                 fecha_asignacion=None, id=None):
        self.id = id
        self.id_empleado = id_empleado
        self.id_proyecto = id_proyecto
        self.rol_proyecto = rol_proyecto
        self.horas_asignadas = horas_asignadas
        self.fecha_asignacion = fecha_asignacion or date.today()

    @property
    def rol_proyecto(self):
        return self.__rol

    @rol_proyecto.setter
    def rol_proyecto(self, v):
        self.__rol = texto_requerido(v, "El rol en el proyecto", 2, 60)

    @property
    def horas_asignadas(self):
        return self.__horas

    @horas_asignadas.setter
    def horas_asignadas(self, v):
        self.__horas = numero(v, "Las horas asignadas", minimo=0, maximo=10000, estricto_minimo=True)

    @property
    def fecha_asignacion(self):
        return self.__fecha

    @fecha_asignacion.setter
    def fecha_asignacion(self, v):
        self.__fecha = parsear_fecha(v, "La fecha de asignación")

    def __str__(self):
        return f"[{self.id}] emp {self.id_empleado} -> proy {self.id_proyecto} ({self.rol_proyecto})"
