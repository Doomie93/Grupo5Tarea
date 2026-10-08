from modelo.registro_tiempo import RegistroTiempo

from .dao_base import DAOBase


class DAORegistro(DAOBase):
    TABLA = "registro_tiempo"
    ENTIDAD = "un registro de horas"

    def _mapear(self, f):
        return RegistroTiempo(f["id_asignacion"], f["fecha"], f["horas"], f["descripcion"], f["id"])

    def crear(self, r):
        r.id = self._cx.ejecutar(
            "INSERT INTO registro_tiempo (id_asignacion, fecha, horas, descripcion) VALUES (?,?,?,?)",
            (r.id_asignacion, r.fecha.isoformat(), r.horas, r.descripcion)).lastrowid
        return r

    def actualizar(self, r):
        cur = self._cx.ejecutar(
            "UPDATE registro_tiempo SET fecha=?, horas=?, descripcion=? WHERE id=?",
            (r.fecha.isoformat(), r.horas, r.descripcion, r.id))
        self._verificar_actualizacion(cur, r.id)

    def listar_por_asignacion(self, id_asignacion):
        filas = self._cx.consultar_todos(
            "SELECT * FROM registro_tiempo WHERE id_asignacion = ? ORDER BY fecha, id", (id_asignacion,))
        return [self._mapear(f) for f in filas]

    def total_horas_asignacion(self, id_asignacion):
        return self._cx.consultar_uno(
            "SELECT COALESCE(SUM(horas), 0) AS t FROM registro_tiempo WHERE id_asignacion = ?",
            (id_asignacion,))["t"]

    # ---------- Reportes ----------
    def horas_por_proyecto(self):
        return [dict(f) for f in self._cx.consultar_todos(
            "SELECT p.nombre AS proyecto, p.estado, COALESCE(SUM(r.horas), 0) AS horas, "
            "COALESCE((SELECT SUM(horas_asignadas) FROM asignacion_proyecto WHERE id_proyecto = p.id), 0) "
            "AS horas_asignadas "
            "FROM proyecto p "
            "LEFT JOIN asignacion_proyecto a ON a.id_proyecto = p.id "
            "LEFT JOIN registro_tiempo r ON r.id_asignacion = a.id "
            "GROUP BY p.id ORDER BY horas DESC")]

    def horas_por_empleado(self):
        return [dict(f) for f in self._cx.consultar_todos(
            "SELECT e.nombre AS empleado, COALESCE(SUM(r.horas), 0) AS horas "
            "FROM empleado e "
            "LEFT JOIN asignacion_proyecto a ON a.id_empleado = e.id "
            "LEFT JOIN registro_tiempo r ON r.id_asignacion = a.id "
            "WHERE e.activo = 1 GROUP BY e.id ORDER BY horas DESC")]
