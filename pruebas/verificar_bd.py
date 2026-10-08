"""Verifica la conexión y el esquema de la BD.   Uso:  python -m pruebas.verificar_bd"""
import sys

from conex.conexion import Conexion
from dao.excepciones import EcoTechError

TABLAS = ["departamento", "empleado", "usuario", "proyecto", "asignacion_proyecto", "registro_tiempo"]


def main():
    try:
        with Conexion() as cx:
            print(f"✓ Conexión OK -> {cx.ruta}")
            fk = cx.consultar_uno("PRAGMA foreign_keys")[0]
            print(f"{'✓' if fk else '✗'} Claves foráneas {'activas' if fk else 'DESACTIVADAS'}")
            for t in TABLAS:
                n = cx.consultar_uno(f"SELECT COUNT(*) AS n FROM {t}")["n"]
                print(f"✓ Tabla {t:<22} {n} registro(s)")
        return 0
    except EcoTechError as e:
        print(f"✗ {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
