from dao.excepciones import PermisoError, ValidacionError
from modelo.asignacion_proyecto import AsignacionProyecto
from modelo.usuario import ADMIN, EMPLEADO, GERENTE

from .controlador_base import ControladorBase


class ControladorAsignacion(ControladorBase):
    def __init__(self, sesion, dao_asignacion, dao_empleado, dao_proyecto):
        super().__init__(sesion)
        self._dao = dao_asignacion
        self._dao_emp = dao_empleado
        self._dao_proy = dao_proyecto

    def asignar(self, id_empleado, id_proyecto, rol_proyecto, horas_asignadas):
        self._exigir(ADMIN, GERENTE)
        emp = self._dao_emp.obtener(id_empleado)
        proy = self._dao_proy.obtener(id_proyecto)
        if not emp.activo:
            raise ValidacionError("No se puede asignar a un empleado dado de baja.")
        if not proy.acepta_asignaciones():
            raise ValidacionError(f"El proyecto está {proy.estado}; no admite nuevas asignaciones.")
        return self._dao.crear(AsignacionProyecto(id_empleado, id_proyecto, rol_proyecto, horas_asignadas))

    def listar(self):
        self._exigir(ADMIN, GERENTE)
        return self._dao.listar_detalle()

    def listar_mias(self):
        u = self._exigir(ADMIN, GERENTE, EMPLEADO)
        if u.id_empleado is None:
            raise PermisoError("Su usuario no está vinculado a un empleado.")
        return self._dao.listar_detalle(u.id_empleado)

    def actualizar(self, id_asignacion, rol_proyecto=None, horas_asignadas=None):
        self._exigir(ADMIN, GERENTE)
        a = self._dao.obtener(id_asignacion)
        if rol_proyecto:
            a.rol_proyecto = rol_proyecto
        if horas_asignadas is not None:
            a.horas_asignadas = horas_asignadas
        self._dao.actualizar(a)
        return a

    def eliminar(self, id_asignacion):
        """Elimina también sus registros de horas (ON DELETE CASCADE)."""
        self._exigir(ADMIN, GERENTE)
        self._dao.eliminar(id_asignacion)
