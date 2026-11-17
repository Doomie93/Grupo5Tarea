import logging
from datetime import date, datetime
from servicios.http_seguro import obtenerJson, ErrorServicio

log = logging.getLogger("ecotech.servicios")

# Se prueban en orden: si findic.cl falla (error de red, 5xx, JSON inválido) se usa mindicador.cl
FUENTES = [("findic.cl", "https://findic.cl/api"),
           ("mindicador.cl", "https://mindicador.cl/api")]

# Lista blanca de indicadores: el código que llega a la URL nunca viene directo del usuario
INDICADORES = {"uf": "UF", "dolar": "Dólar", "euro": "Euro", "utm": "UTM"}
INDICADORES_MENSUALES = ("utm",)         # la API publica un valor por mes (día 1)

MAX_ANIOS_RANGO = 5


# Convierte la serie del JSON en una lista de (fecha, valor), ignorando elementos mal formados
def _parsearSerie(datos: dict) -> list:
    serie = datos.get("serie")
    if not isinstance(serie, list):
        raise ErrorServicio("El servicio externo entregó una respuesta inválida.")
    resultado = []
    for item in serie:
        try:
            fecha = datetime.strptime(str(item["fecha"])[:10], "%Y-%m-%d").date()   # "2026-01-15T03:00:00.000Z" -> 2026-01-15
            valor = float(item["valor"])
        except (KeyError, TypeError, ValueError):
            continue
        resultado.append((fecha, valor))
    return resultado


# Consulta una ruta (ej: "uf/15-01-2026") probando cada fuente. Retorna (autor, [(fecha, valor)]).
def _consultar(ruta: str) -> tuple:
    for autor, base in FUENTES:
        try:
            return autor, _parsearSerie(obtenerJson(f"{base}/{ruta}"))
        except ErrorServicio as ex:
            log.warning("Fuente %s falló para '%s': %s", autor, ruta, ex)
    raise ErrorServicio("No fue posible obtener el indicador: ninguna fuente respondió correctamente.")


def _validarCodigo(codigo: str) -> None:
    if codigo not in INDICADORES:
        raise ErrorServicio("Indicador no válido.")


# Valor más reciente publicado. Retorna lista de dict {autor, fecha, valor} (vacía si no hay datos)
def obtenerUltimo(codigo: str) -> list:
    _validarCodigo(codigo)
    autor, serie = _consultar(codigo)
    if not serie:
        return []
    fecha, valor = max(serie, key=lambda p: p[0])
    return [{"autor": autor, "fecha": fecha, "valor": valor}]


# Valor de una fecha puntual
def obtenerPorFecha(codigo: str, fecha: date) -> list:
    _validarCodigo(codigo)
    if codigo in INDICADORES_MENSUALES:
        fecha = fecha.replace(day=1)
    autor, serie = _consultar(f"{codigo}/{fecha.strftime('%d-%m-%Y')}")
    return [{"autor": autor, "fecha": f, "valor": v} for f, v in serie if f == fecha]


# Valores entre dos fechas (inclusive). La API entrega un año completo por consulta, luego se filtra.
def obtenerRango(codigo: str, desde: date, hasta: date) -> list:
    _validarCodigo(codigo)
    if desde > hasta:
        raise ErrorServicio("La fecha inicial no puede ser posterior a la final.")
    if hasta.year - desde.year + 1 > MAX_ANIOS_RANGO:
        raise ErrorServicio(f"El rango no puede abarcar más de {MAX_ANIOS_RANGO} años.")
    if codigo in INDICADORES_MENSUALES:
        desde = desde.replace(day=1)
    resultado = []
    for anio in range(desde.year, hasta.year + 1):
        autor, serie = _consultar(f"{codigo}/{anio}")
        resultado += [{"autor": autor, "fecha": f, "valor": v} for f, v in serie if desde <= f <= hasta]
    resultado.sort(key=lambda r: r["fecha"])
    return resultado
