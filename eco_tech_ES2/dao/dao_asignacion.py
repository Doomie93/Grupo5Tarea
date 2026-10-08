from modelo.asignacion_proyecto import AsignacionProyecto

from .dao_base import DAOBase


class DAOAsignacion(DAOBase):
    TABLA = "asignacion_proyecto"
    ENTIDAD = "una asignación"

    def _mapear(self, f):
        return AsignacionProyecto(f["id_empleado"], f["id_proyecto"], f["rol_proyecto"],
                                  f["horas_asignadas"], f["fecha_asignacion"], f["id"])

    def crear(self, a):
        a.id = self._cx.ejecutar(
            "INSERT INTO asignacion_proyecto (id_empleado, id_proyecto, rol_proyecto, horas_asignadas, "
            "fecha_asignacion) VALUES (?,?,?,?,?)",
            (a.id_empleado, a.id_proyecto, a.rol_proyecto, a.horas_asignadas,
             a.fecha_asignacion.isoformat())).lastrowid
        return a

    def actualizar(self, a):
        cur = self._cx.ejecutar(
            "UPDATE asignacion_proyecto SET rol_proyecto=?, horas_asignadas=? WHERE id=?",
            (a.rol_proyecto, a.horas_asignadas, a.id))
        self._verificar_actualizacion(cur, a.id)

    def listar_por_empleado(self, id_empleado):
        filas = self._cx.consultar_todos(
            "SELECT * FROM asignacion_proyecto WHERE id_empleado = ? ORDER BY id", (id_empleado,))
        return [self._mapear(f) for f in filas]

    def listar_por_proyecto(self, id_proyecto):
        filas = self._cx.consultar_todos(
            "SELECT * FROM asignacion_proyecto WHERE id_proyecto = ? ORDER BY id", (id_proyecto,))
        return [self._mapear(f) for f in filas]

    def listar_detalle(self, id_empleado=None):
        """Filas con nombres legibles (JOIN) para mostrar en pantalla."""
        sql = ("SELECT a.id, e.nombre AS empleado, p.nombre AS proyecto, a.rol_proyecto, "
               "a.horas_asignadas, COALESCE(SUM(r.horas), 0) AS horas_registradas "
               "FROM asignacion_proyecto a "
               "JOIN empleado e ON e.id = a.id_empleado "
               "JOIN proyecto p ON p.id = a.id_proyecto "
               "LEFT JOIN registro_tiempo r ON r.id_asignacion = a.id ")
        params = ()
        if id_empleado is not None:
            sql += "WHERE a.id_empleado = ? "
            params = (id_empleado,)
        sql += "GROUP BY a.id ORDER BY a.id"
        return [dict(f) for f in self._cx.consultar_todos(sql, params)]
