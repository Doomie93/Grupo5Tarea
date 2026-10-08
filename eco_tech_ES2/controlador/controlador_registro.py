from dao.excepciones import PermisoError, ValidacionError
from modelo.registro_tiempo import RegistroTiempo
from modelo.usuario import ADMIN, EMPLEADO, GERENTE

from .controlador_base import ControladorBase


class ControladorRegistro(ControladorBase):
    def __init__(self, sesion, dao_registro, dao_asignacion):
        super().__init__(sesion)
        self._dao = dao_registro
        self._dao_asig = dao_asignacion

    def _validar_propiedad(self, usuario, asignacion):
        if usuario.rol == EMPLEADO and asignacion.id_empleado != usuario.id_empleado:
            raise PermisoError("Solo puede operar sobre sus propias asignaciones.")

    def registrar(self, id_asignacion, fecha, horas, descripcion=""):
        u = self._exigir(ADMIN, GERENTE, EMPLEADO)
        asig = self._dao_asig.obtener(id_asignacion)
        self._validar_propiedad(u, asig)
        r = RegistroTiempo(id_asignacion, fecha, horas, descripcion)  # valida fecha/horas
        acumulado = self._dao.total_horas_asignacion(id_asignacion)
        if acumulado + r.horas > asig.horas_asignadas:
            raise ValidacionError(
                f"Excede las horas asignadas ({acumulado:g} registradas + {r.horas:g} > {asig.horas_asignadas:g}).")
        return self._dao.crear(r)

    def listar_por_asignacion(self, id_asignacion):
        u = self._exigir(ADMIN, GERENTE, EMPLEADO)
        self._validar_propiedad(u, self._dao_asig.obtener(id_asignacion))
        return self._dao.listar_por_asignacion(id_asignacion)

    def eliminar(self, id_registro):
        u = self._exigir(ADMIN, GERENTE, EMPLEADO)
        reg = self._dao.obtener(id_registro)
        self._validar_propiedad(u, self._dao_asig.obtener(reg.id_asignacion))
        self._dao.eliminar(id_registro)

    # ---------- Reportes (solo supervisión) ----------
    def reporte_horas_por_proyecto(self):
        self._exigir(ADMIN, GERENTE)
        return self._dao.horas_por_proyecto()

    def reporte_horas_por_empleado(self):
        self._exigir(ADMIN, GERENTE)
        return self._dao.horas_por_empleado()
