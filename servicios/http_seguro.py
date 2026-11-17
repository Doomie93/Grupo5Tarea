import logging
import requests

# Los detalles técnicos (URL, excepción, código HTTP) van al archivo de log; el usuario solo ve mensajes genéricos.
log = logging.getLogger("ecotech.servicios")

TIMEOUT = (3, 8)                    # (segundos para conectar, segundos para leer la respuesta)
MAX_BYTES = 2 * 1024 * 1024         # se descarta cualquier respuesta de más de 2 MB
CABECERAS = {"Accept": "application/json", "User-Agent": "EcoTech-Solutions/1.0"}


class ErrorServicio(Exception):
    """Fallo al consumir un servicio externo. El texto de esta excepción ES seguro de mostrar al usuario."""
    pass


# Hace un GET y retorna el JSON ya convertido a dict. Cualquier problema se traduce a ErrorServicio.
def obtenerJson(url: str, params: dict = None) -> dict:
    try:
        # verify=True (por defecto): nunca se desactiva la validación del certificado TLS
        resp = requests.get(url, params=params, headers=CABECERAS, timeout=TIMEOUT)
    except requests.exceptions.Timeout:
        log.warning("Timeout al consultar %s", url)
        raise ErrorServicio("El servicio externo tardó demasiado en responder.")
    except requests.exceptions.SSLError:
        log.error("Error de certificado SSL al consultar %s", url)
        raise ErrorServicio("No se pudo establecer una conexión segura con el servicio externo.")
    except requests.exceptions.ConnectionError:
        log.warning("Sin conexión al consultar %s", url)
        raise ErrorServicio("No hay conexión con el servicio externo. Revise su acceso a Internet.")
    except requests.exceptions.RequestException as ex:
        log.error("Error de requests al consultar %s: %r", url, ex)
        raise ErrorServicio("No se pudo completar la consulta al servicio externo.")

    codigo = resp.status_code
    if codigo != 200:
        log.warning("HTTP %s al consultar %s", codigo, url)
        if codigo == 404:
            raise ErrorServicio("El servicio externo no encontró lo solicitado.")
        if codigo == 429:
            raise ErrorServicio("Se superó el límite de consultas del servicio externo. Intente más tarde.")
        if 500 <= codigo <= 599:
            raise ErrorServicio("El servicio externo no está disponible en este momento.")
        raise ErrorServicio("El servicio externo respondió con un error inesperado.")

    if len(resp.content) > MAX_BYTES:
        log.error("Respuesta demasiado grande (%s bytes) desde %s", len(resp.content), url)
        raise ErrorServicio("El servicio externo entregó una respuesta inválida.")
    try:
        datos = resp.json()
    except ValueError:
        log.error("Respuesta no JSON desde %s", url)
        raise ErrorServicio("El servicio externo entregó una respuesta inválida.")
    if not isinstance(datos, dict):
        log.error("JSON con estructura inesperada desde %s", url)
        raise ErrorServicio("El servicio externo entregó una respuesta inválida.")
    return datos
