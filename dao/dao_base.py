"""Clase base de los DAO (Data Access Object).

Implementa lo común (obtener, listar, eliminar, contar) y obliga a cada DAO
concreto a definir crear, actualizar y cómo convertir una fila en objeto.
"""
from abc import ABC, abstractmethod

from .excepciones import NoEncontradoError


class DAOBase(ABC):
    TABLA = None      # constante interna (nunca proviene del usuario)
    ENTIDAD = "registro"

    def __init__(self, conexion):
        self._cx = conexion

    @abstractmethod
    def _mapear(self, fila):
        """Convierte una fila de la BD en un objeto del modelo."""

    @abstractmethod
    def crear(self, obj):
        ...

    @abstractmethod
    def actualizar(self, obj):
        ...

    def obtener(self, id):
        fila = self._cx.consultar_uno(f"SELECT * FROM {self.TABLA} WHERE id = ?", (id,))
        if fila is None:
            raise NoEncontradoError(f"No existe {self.ENTIDAD} con id {id}.")
        return self._mapear(fila)

    def listar(self):
        filas = self._cx.consultar_todos(f"SELECT * FROM {self.TABLA} ORDER BY id")
        return [self._mapear(f) for f in filas]

    def eliminar(self, id):
        cur = self._cx.ejecutar(f"DELETE FROM {self.TABLA} WHERE id = ?", (id,))
        if cur.rowcount == 0:
            raise NoEncontradoError(f"No existe {self.ENTIDAD} con id {id}.")

    def contar(self):
        return self._cx.consultar_uno(f"SELECT COUNT(*) AS n FROM {self.TABLA}")["n"]

    def _verificar_actualizacion(self, cursor, id):
        if cursor.rowcount == 0:
            raise NoEncontradoError(f"No existe {self.ENTIDAD} con id {id}.")
