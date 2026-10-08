from modelo.proyecto import Proyecto

from .dao_base import DAOBase


class DAOProyecto(DAOBase):
    TABLA = "proyecto"
    ENTIDAD = "un proyecto"

    def _mapear(self, f):
        return Proyecto(f["nombre"], f["fecha_inicio"], f["descripcion"], f["fecha_fin"],
                        f["estado"], f["presupuesto"], f["id"])

    @staticmethod
    def _params(p):
        return (p.nombre, p.descripcion, p.fecha_inicio.isoformat(),
                p.fecha_fin.isoformat() if p.fecha_fin else None, p.estado, p.presupuesto)

    def crear(self, p):
        p.id = self._cx.ejecutar(
            "INSERT INTO proyecto (nombre, descripcion, fecha_inicio, fecha_fin, estado, presupuesto) "
            "VALUES (?,?,?,?,?,?)", self._params(p)).lastrowid
        return p

    def actualizar(self, p):
        cur = self._cx.ejecutar(
            "UPDATE proyecto SET nombre=?, descripcion=?, fecha_inicio=?, fecha_fin=?, estado=?, "
            "presupuesto=? WHERE id=?", self._params(p) + (p.id,))
        self._verificar_actualizacion(cur, p.id)

    def listar_por_estado(self, estado):
        filas = self._cx.consultar_todos("SELECT * FROM proyecto WHERE estado = ? ORDER BY id", (estado,))
        return [self._mapear(f) for f in filas]
