"""Conexión a la base de datos (sqlite3, librería oficial de Python).

Centraliza: apertura, creación del esquema, transacciones y traducción de
errores de sqlite3 a excepciones propias. Los DAO nunca tocan sqlite3.
"""
import os
import sqlite3

from dao.excepciones import BaseDatosError, DuplicadoError

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUTA_ESQUEMA = os.path.join(RAIZ, "base_datos", "ecotech_gestion.sql")
RUTA_DEFECTO = os.path.join(RAIZ, "base_datos", "ecotech_gestion.db")


class Conexion:
    def __init__(self, ruta=None):
        # La ruta puede venir por parámetro o por variable de entorno ECOTECH_DB
        self._ruta = ruta or os.environ.get("ECOTECH_DB", RUTA_DEFECTO)
        try:
            self._con = sqlite3.connect(self._ruta)
            self._con.row_factory = sqlite3.Row
            self._con.execute("PRAGMA foreign_keys = ON")
            self._crear_esquema()
        except (sqlite3.Error, OSError) as e:
            raise BaseDatosError(f"No se pudo conectar a la base de datos: {e}") from e

    @property
    def ruta(self):
        return self._ruta

    def _crear_esquema(self):
        with open(RUTA_ESQUEMA, encoding="utf-8") as f:
            self._con.executescript(f.read())

    @staticmethod
    def _traducir(e):
        msg = str(e)
        if "UNIQUE" in msg:
            return DuplicadoError("Ya existe un registro con ese valor único (RUT, correo, nombre o usuario).")
        if "FOREIGN KEY" in msg:
            return BaseDatosError("Operación rechazada: el registro está relacionado con otros datos "
                                  "o referencia algo que no existe.")
        if "CHECK" in msg:
            return BaseDatosError("Un valor está fuera del rango permitido por la base de datos.")
        return BaseDatosError(f"Violación de integridad: {msg}")

    def ejecutar(self, sql, params=()):
        """INSERT/UPDATE/DELETE con commit automático (rollback si falla)."""
        try:
            with self._con:
                return self._con.execute(sql, params)
        except sqlite3.IntegrityError as e:
            raise self._traducir(e) from e
        except sqlite3.Error as e:
            raise BaseDatosError(f"Error de base de datos: {e}") from e

    def consultar_uno(self, sql, params=()):
        try:
            return self._con.execute(sql, params).fetchone()
        except sqlite3.Error as e:
            raise BaseDatosError(f"Error de consulta: {e}") from e

    def consultar_todos(self, sql, params=()):
        try:
            return self._con.execute(sql, params).fetchall()
        except sqlite3.Error as e:
            raise BaseDatosError(f"Error de consulta: {e}") from e

    def cerrar(self):
        try:
            self._con.close()
        except sqlite3.Error:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.cerrar()
