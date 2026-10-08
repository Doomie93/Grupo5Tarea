from modelo.departamento import Departamento

from .dao_base import DAOBase


class DAODepartamento(DAOBase):
    TABLA = "departamento"
    ENTIDAD = "un departamento"

    def _mapear(self, f):
        return Departamento(f["nombre"], f["descripcion"], f["id"])

    def crear(self, d):
        d.id = self._cx.ejecutar("INSERT INTO departamento (nombre, descripcion) VALUES (?, ?)",
                                 (d.nombre, d.descripcion)).lastrowid
        return d

    def actualizar(self, d):
        cur = self._cx.ejecutar("UPDATE departamento SET nombre = ?, descripcion = ? WHERE id = ?",
                                (d.nombre, d.descripcion, d.id))
        self._verificar_actualizacion(cur, d.id)

    def cantidad_empleados(self):
        """{id_departamento: n_empleados_activos}"""
        filas = self._cx.consultar_todos(
            "SELECT id_departamento AS d, COUNT(*) AS n FROM empleado "
            "WHERE activo = 1 AND id_departamento IS NOT NULL GROUP BY id_departamento")
        return {f["d"]: f["n"] for f in filas}
