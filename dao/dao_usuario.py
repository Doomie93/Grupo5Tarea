from modelo.usuario import Usuario

from .dao_base import DAOBase
from .excepciones import NoEncontradoError


class DAOUsuario(DAOBase):
    TABLA = "usuario"
    ENTIDAD = "un usuario"

    def _mapear(self, f):
        return Usuario(f["username"], f["password_hash"], f["rol"], f["id_empleado"], f["activo"], f["id"])

    def crear(self, u):
        u.id = self._cx.ejecutar(
            "INSERT INTO usuario (username, password_hash, rol, id_empleado, activo) VALUES (?,?,?,?,?)",
            (u.username, u.password_hash, u.rol, u.id_empleado, int(u.activo))).lastrowid
        return u

    def actualizar(self, u):
        cur = self._cx.ejecutar(
            "UPDATE usuario SET password_hash=?, rol=?, id_empleado=?, activo=? WHERE id=?",
            (u.password_hash, u.rol, u.id_empleado, int(u.activo), u.id))
        self._verificar_actualizacion(cur, u.id)

    def obtener_por_username(self, username):
        f = self._cx.consultar_uno("SELECT * FROM usuario WHERE username = ?", (username.strip().lower(),))
        if f is None:
            raise NoEncontradoError("Usuario no encontrado.")
        return self._mapear(f)

    def contar_admins_activos(self):
        return self._cx.consultar_uno(
            "SELECT COUNT(*) AS n FROM usuario WHERE rol='ADMIN' AND activo=1")["n"]
