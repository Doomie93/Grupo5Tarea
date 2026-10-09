import pymysql as conn
from pymysql.constants import CLIENT


class Conex:

    def __init__(self, host, user, passwd, database=None):
        self.__myconn = None
        self.__error = ""
        try:
            # FOUND_ROWS: rowcount cuenta las filas encontradas aunque el UPDATE no cambie valores
            self.__myconn = conn.connect(host=host,
                                         user=user,
                                         passwd=passwd,
                                         database=database,
                                         charset="utf8mb4",
                                         connect_timeout=5,
                                         client_flag=CLIENT.FOUND_ROWS,
                                         cursorclass=conn.cursors.DictCursor)
        except Exception as ex:
            self.__error = str(ex)
            self.__myconn = None

    def estaConectado(self) -> bool:
        return self.__myconn is not None

    def getError(self) -> str:
        return self.__error

    def closeConex(self) -> None:
        if self.__myconn is not None:
            try:
                self.__myconn.close()
            except Exception:
                pass
            self.__myconn = None

    def getConex(self):
        return self.__myconn
