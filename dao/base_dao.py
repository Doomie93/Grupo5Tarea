from conex.conn import Conex
from conex import config

# Códigos de resultado (los valores > 0 indican filas afectadas)
ERROR_GENERAL = -1
ERROR_DUPLICADO = -2
ERROR_RELACION = -3
ERROR_CONEXION = -4


class BaseDAO():
    """Clase base de los DAO: centraliza la conexión, la ejecución de SQL y el manejo de errores,
    evitando repetir el mismo bloque try/except/finally en cada DAO."""

    # Constructor
    def __init__(self, database: str = config.DATABASE) -> None:
        self._database = database
        self._ultimoId = 0

    def getUltimoId(self) -> int:
        return self._ultimoId

    # Abre una conexión nueva (se cierra al terminar cada operación)
    def _abrir(self) -> Conex:
        return Conex(config.HOST, config.USER, config.PASSWD, self._database)

    # Verifica que se pueda entrar a la base de datos (debe existir de antes, ver mydb_ecotech.txt)
    def probarConexion(self) -> bool:
        c = self._abrir()
        if not c.estaConectado():
            print("-No se pudo conectar a la base de datos-")
            print("-Verifique que MySQL esté activo en XAMPP, que la base exista (script mydb_ecotech.txt)")
            print(" y que las credenciales de conex/config.py sean correctas-")
            print(f"-Detalle: {c.getError()}-")
            return False
        c.closeConex()
        return True

    # Clasifica el error de MySQL según su código
    @staticmethod
    def _clasificarError(ex: Exception) -> int:
        codigo = ex.args[0] if ex.args and isinstance(ex.args[0], int) else 0
        if codigo == 1062:
            return ERROR_DUPLICADO
        if codigo in (1451, 1452):
            return ERROR_RELACION
        if codigo in (1045, 2002, 2003, 2006, 2013):
            return ERROR_CONEXION
        return ERROR_GENERAL

    # INSERT / UPDATE / DELETE -> retorna filas afectadas o un código de error negativo
    def _ejecutar(self, sql: str, params: tuple = ()) -> int:
        self._ultimoId = 0
        c = self._abrir()
        if not c.estaConectado():
            return ERROR_CONEXION
        try:
            cursor = c.getConex().cursor()
            cursor.execute(sql, params)
            c.getConex().commit()
            self._ultimoId = cursor.lastrowid
            return cursor.rowcount
        except Exception as ex:
            try:
                c.getConex().rollback()
            except Exception:
                pass
            return self._clasificarError(ex)
        finally:
            c.closeConex()

    # SELECT -> retorna lista de diccionarios (None si hubo un problema)
    def _consultar(self, sql: str, params: tuple = ()) -> list:
        c = self._abrir()
        if not c.estaConectado():
            print("-No hay conexión con la base de datos. Verifique que MySQL esté activo en XAMPP-")
            return None
        try:
            cursor = c.getConex().cursor()
            cursor.execute(sql, params)
            return cursor.fetchall()
        except Exception as ex:
            print(f"-Problemas con la base de datos: {ex}-")
            return None
        finally:
            c.closeConex()
