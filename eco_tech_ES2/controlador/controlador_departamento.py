from modelo.departamento import Departamento
from modelo.usuario import ADMIN, EMPLEADO, GERENTE

from .controlador_base import ControladorBase


class ControladorDepartamento(ControladorBase):
    def __init__(self, sesion, dao):
        super().__init__(sesion)
        self._dao = dao

    def crear(self, nombre, descripcion=""):
        self._exigir(ADMIN, GERENTE)
        return self._dao.crear(Departamento(nombre, descripcion))

    def listar(self):
        self._exigir(ADMIN, GERENTE, EMPLEADO)
        return self._dao.listar()

    def listar_con_dotacion(self):
        dot = self._dao.cantidad_empleados()
        return [(d, dot.get(d.id, 0)) for d in self.listar()]

    def actualizar(self, id_depto, nombre=None, descripcion=None):
        self._exigir(ADMIN, GERENTE)
        d = self._dao.obtener(id_depto)
        if nombre:
            d.nombre = nombre
        if descripcion is not None:
            d.descripcion = descripcion
        self._dao.actualizar(d)
        return d

    def eliminar(self, id_depto):
        self._exigir(ADMIN)
        self._dao.eliminar(id_depto)  # la BD rechaza si tiene empleados (RESTRICT)
