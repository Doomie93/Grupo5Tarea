from modelo.proyecto import Proyecto
from modelo.usuario import ADMIN, EMPLEADO, GERENTE

from .controlador_base import ControladorBase


class ControladorProyecto(ControladorBase):
    def __init__(self, sesion, dao):
        super().__init__(sesion)
        self._dao = dao

    def crear(self, nombre, fecha_inicio, descripcion="", fecha_fin=None, presupuesto=0):
        self._exigir(ADMIN, GERENTE)
        return self._dao.crear(Proyecto(nombre, fecha_inicio, descripcion, fecha_fin, "PLANIFICADO", presupuesto))

    def listar(self):
        self._exigir(ADMIN, GERENTE, EMPLEADO)
        return self._dao.listar()

    def obtener(self, id_proyecto):
        self._exigir(ADMIN, GERENTE, EMPLEADO)
        return self._dao.obtener(id_proyecto)

    def actualizar(self, id_proyecto, **campos):
        self._exigir(ADMIN, GERENTE)
        p = self._dao.obtener(id_proyecto)
        for campo, valor in campos.items():
            if campo not in {"nombre", "descripcion", "fecha_fin", "estado", "presupuesto"}:
                continue
            setattr(p, campo, valor)
        self._dao.actualizar(p)
        return p

    def eliminar(self, id_proyecto):
        self._exigir(ADMIN)
        self._dao.eliminar(id_proyecto)
