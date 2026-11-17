from dao.base_dao import BaseDAO
from modelo.indicador import Indicador


class IndicadorDAO(BaseDAO):

    # Guarda los indicadores consultados. Si ya existe (mismo usuario, fuente, código y fecha) actualiza el valor.
    def registrarIndicadores(self, lista: list) -> int:
        sql = ("insert into INDICADOR (IDUSUARIO, AUTOR, CODIGO, FECHA, VALOR) values (%s, %s, %s, %s, %s) "
               "on duplicate key update VALOR = values(VALOR), FECHACONSULTA = current_timestamp")
        return self._ejecutarVarios(sql, [(i.getIdUsuario(), i.getAutor(), i.getCodigo(), i.getFecha(), i.getValor())
                                          for i in lista])

    # Últimos indicadores guardados (opcionalmente de un solo código). None si hubo un problema.
    def listarIndicadores(self, codigo: str = None, limite: int = 30) -> list:
        sql = ("select I.IDINDICADOR, I.IDUSUARIO, I.AUTOR, I.CODIGO, I.FECHA, I.VALOR, U.NOMBREUSUARIO "
               "from INDICADOR I join USUARIO U on U.IDUSUARIO = I.IDUSUARIO ")
        params = []
        if codigo is not None:
            sql += "where I.CODIGO = %s "
            params.append(codigo)
        sql += "order by I.FECHACONSULTA desc, I.FECHA desc limit %s"
        params.append(int(limite))
        filas = self._consultar(sql, tuple(params))
        if filas is None:
            return None
        return [Indicador(f["IDINDICADOR"], f["IDUSUARIO"], f["AUTOR"], f["CODIGO"], f["FECHA"], float(f["VALOR"]),
                          f["NOMBREUSUARIO"]) for f in filas]
