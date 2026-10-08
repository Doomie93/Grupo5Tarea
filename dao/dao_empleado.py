from modelo.empleado import crear_empleado

from .dao_base import DAOBase


class DAOEmpleado(DAOBase):
    TABLA = "empleado"
    ENTIDAD = "un empleado"

    def _mapear(self, f):
        return crear_empleado(f["tipo"], rut=f["rut"], nombre=f["nombre"], email=f["email"],
                              salario_base=f["salario_base"], fecha_ingreso=f["fecha_ingreso"],
                              id_departamento=f["id_departamento"], activo=f["activo"], id=f["id"])

    def crear(self, e):
        e.id = self._cx.ejecutar(
            "INSERT INTO empleado (tipo, rut, nombre, email, salario_base, fecha_ingreso, "
            "id_departamento, activo) VALUES (?,?,?,?,?,?,?,?)",
            (e.TIPO, e.rut, e.nombre, e.email, e.salario_base, e.fecha_ingreso.isoformat(),
             e.id_departamento, int(e.activo))).lastrowid
        return e

    def actualizar(self, e):
        cur = self._cx.ejecutar(
            "UPDATE empleado SET rut=?, nombre=?, email=?, salario_base=?, fecha_ingreso=?, "
            "id_departamento=?, activo=? WHERE id=?",
            (e.rut, e.nombre, e.email, e.salario_base, e.fecha_ingreso.isoformat(),
             e.id_departamento, int(e.activo), e.id))
        self._verificar_actualizacion(cur, e.id)

    def listar_activos(self):
        filas = self._cx.consultar_todos("SELECT * FROM empleado WHERE activo = 1 ORDER BY id")
        return [self._mapear(f) for f in filas]

    def listar_por_departamento(self, id_departamento):
        filas = self._cx.consultar_todos(
            "SELECT * FROM empleado WHERE id_departamento = ? ORDER BY nombre", (id_departamento,))
        return [self._mapear(f) for f in filas]

    def buscar(self, texto):
        patron = f"%{texto.strip()}%"
        filas = self._cx.consultar_todos(
            "SELECT * FROM empleado WHERE nombre LIKE ? OR rut LIKE ? OR email LIKE ? ORDER BY nombre",
            (patron, patron, patron))
        return [self._mapear(f) for f in filas]
