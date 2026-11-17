import re
from servicios.http_seguro import obtenerJson, ErrorServicio

# Open-Meteo: gratuita y sin llave de API (no hay credenciales que proteger). Si se cambiara por una API con llave
# (ej. OpenWeatherMap), la llave debe leerse con os.environ.get("CLIMA_API_KEY") y nunca escribirse en el código.
URL_GEOCODIFICACION = "https://geocoding-api.open-meteo.com/v1/search"
URL_PRONOSTICO = "https://api.open-meteo.com/v1/forecast"

# Descripción de los códigos WMO que entrega la API
ESTADOS = {0: "Despejado", 1: "Mayormente despejado", 2: "Parcialmente nublado", 3: "Nublado",
           45: "Niebla", 48: "Niebla con escarcha",
           51: "Llovizna ligera", 53: "Llovizna moderada", 55: "Llovizna intensa",
           56: "Llovizna helada", 57: "Llovizna helada intensa",
           61: "Lluvia ligera", 63: "Lluvia moderada", 65: "Lluvia intensa",
           66: "Lluvia helada", 67: "Lluvia helada intensa",
           71: "Nieve ligera", 73: "Nieve moderada", 75: "Nieve intensa", 77: "Granizo fino",
           80: "Chubascos ligeros", 81: "Chubascos moderados", 82: "Chubascos violentos",
           85: "Chubascos de nieve", 86: "Chubascos de nieve intensos",
           95: "Tormenta eléctrica", 96: "Tormenta con granizo", 99: "Tormenta con granizo fuerte"}
# Umbrales de decisión (ajustables)
UMBRAL_SOLAR_ALTO = 5.0      # kWh/m² al día
UMBRAL_SOLAR_MEDIO = 3.0
RAFAGAS_MAX_KMH = 50
LLUVIA_MAX_PROB = 60
UV_ALTO = 8


# Validaciones de entrada (se aplican antes de llamar a la API)
def validarCiudad(ciudad: str) -> bool:
    ciudad = ciudad.strip()
    return 2 <= len(ciudad) <= 60 and re.fullmatch(r"[^\W\d_]+(?:[ .'\-][^\W\d_]+)*", ciudad) is not None


def validarPais(pais: str) -> bool:
    return re.fullmatch(r"[A-Za-z]{2}", pais.strip()) is not None


def _numero(valor, minimo: float, maximo: float) -> float:
    if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not (minimo <= valor <= maximo):
        raise ErrorServicio("El servicio externo entregó datos climáticos inválidos.")
    return float(valor)


# Busca la ciudad y retorna {"nombre", "region", "pais", "latitud", "longitud"}
def buscarCiudad(ciudad: str, codigoPais: str = "") -> dict:
    if not validarCiudad(ciudad) or (codigoPais and not validarPais(codigoPais)):
        raise ErrorServicio("Ciudad o país inválido.")
    params = {"name": ciudad.strip(), "count": 1, "language": "es", "format": "json"}
    if codigoPais:
        params["countryCode"] = codigoPais.strip().upper()
    resultados = obtenerJson(URL_GEOCODIFICACION, params).get("results")
    if not isinstance(resultados, list) or not resultados or not isinstance(resultados[0], dict):
        raise ErrorServicio("No se encontró esa ciudad. Revise el nombre o indique el país.")
    r = resultados[0]
    return {"nombre": str(r.get("name", ciudad)), "region": str(r.get("admin1", "")), "pais": str(r.get("country", "")),
            "latitud": _numero(r.get("latitude"), -90, 90), "longitud": _numero(r.get("longitude"), -180, 180)}


# Clima actual + pronóstico de 3 días con variables útiles para energía solar y trabajos de terreno
def obtenerClima(ciudad: str, codigoPais: str = "") -> dict:
    lugar = buscarCiudad(ciudad, codigoPais)
    datos = obtenerJson(URL_PRONOSTICO, {
        "latitude": lugar["latitud"], "longitude": lugar["longitud"], "timezone": "auto", "forecast_days": 3,
        "current": "temperature_2m,relative_humidity_2m,precipitation,weather_code,wind_speed_10m,cloud_cover,shortwave_radiation",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,"
                 "shortwave_radiation_sum,sunshine_duration,uv_index_max,wind_gusts_10m_max"})
    actual, diario = datos.get("current"), datos.get("daily")
    if not isinstance(actual, dict) or not isinstance(diario, dict):
        raise ErrorServicio("El servicio externo entregó una respuesta inválida.")
    codigo = int(_numero(actual.get("weather_code"), 0, 99))
    clima = {"lugar": lugar,
             "temperatura": _numero(actual.get("temperature_2m"), -90, 70),
             "humedad": _numero(actual.get("relative_humidity_2m"), 0, 100),
             "precipitacion": _numero(actual.get("precipitation"), 0, 1000),
             "viento": _numero(actual.get("wind_speed_10m"), 0, 500),
             "nubosidad": _numero(actual.get("cloud_cover"), 0, 100),
             "radiacion": _numero(actual.get("shortwave_radiation"), 0, 1500),      # W/m² en este momento
             "estado": ESTADOS.get(codigo, "Sin descripción"), "codigo": codigo, "pronostico": []}
    try:
        for i, dia in enumerate(diario["time"]):
            clima["pronostico"].append({
                "fecha": str(dia),
                "estado": ESTADOS.get(int(diario["weather_code"][i]), "Sin descripción"),
                "minima": _numero(diario["temperature_2m_min"][i], -90, 70),
                "maxima": _numero(diario["temperature_2m_max"][i], -90, 70),
                "lluvia": diario["precipitation_probability_max"][i],
                "energia": _numero(diario["shortwave_radiation_sum"][i], 0, 60) / 3.6,   # MJ/m² -> kWh/m² del día
                "sol": _numero(diario["sunshine_duration"][i], 0, 90000) / 3600,         # segundos -> horas de sol
                "uv": _numero(diario["uv_index_max"][i], 0, 20),
                "rafagas": _numero(diario["wind_gusts_10m_max"][i], 0, 500)})
    except (KeyError, IndexError, TypeError, ValueError):
        raise ErrorServicio("El servicio externo entregó una respuesta inválida.")
    return clima


# Potencial de generación fotovoltaica según la energía solar diaria (kWh/m²; ~ "horas sol pico")
def potencialSolar(kwhM2: float) -> str:
    if kwhM2 >= UMBRAL_SOLAR_ALTO:
        return "ALTO"
    return "MEDIO" if kwhM2 >= UMBRAL_SOLAR_MEDIO else "BAJO"


# Condiciones para trabajos de instalación/mantención en terreno (techos, paneles, obras)
def aptoParaTrabajoEnTerreno(dia: dict) -> list:
    motivos = []
    if dia["rafagas"] > RAFAGAS_MAX_KMH:
        motivos.append(f"ráfagas de {dia['rafagas']:.0f} km/h (riesgo al trabajar en altura o mover paneles)")
    if isinstance(dia["lluvia"], (int, float)) and dia["lluvia"] >= LLUVIA_MAX_PROB:
        motivos.append(f"probabilidad de lluvia {dia['lluvia']:.0f}% (riesgo eléctrico y superficies resbalosas)")
    if dia["uv"] >= UV_ALTO:
        motivos.append(f"índice UV {dia['uv']:.0f} (exige protección para el personal)")
    return motivos


# Resumen de apoyo a la decisión para proyectos solares y ambientales
def evaluarProyecto(clima: dict) -> list:
    lineas = []
    for d in clima["pronostico"]:
        potencial = potencialSolar(d["energia"])
        motivos = aptoParaTrabajoEnTerreno(d)
        trabajo = "trabajo en terreno posible" if not motivos else "precaución en terreno: " + "; ".join(motivos)
        lineas.append(f"{d['fecha']}: potencial solar {potencial} ({d['energia']:.1f} kWh/m², {d['sol']:.1f} h de sol); {trabajo}.")
    if clima["pronostico"] and all(potencialSolar(d["energia"]) == "BAJO" for d in clima["pronostico"]):
        lineas.append("Varios días con bajo potencial solar: considerar esto al estimar la producción de un sistema fotovoltaico.")
    return lineas
