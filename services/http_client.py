import logging  # Registra incidentes de red en logs/ecotech.log
import requests  # Librería oficial para peticiones HTTP
from requests.adapters import HTTPAdapter  # Configura reintentos en la sesión HTTP
from urllib3.util.retry import Retry  # Define la política de reintentos automáticos
from config.settings import Settings  # Lee el tiempo máximo de espera configurado
from exceptions import (  # Importa nuestras excepciones específicas de red
    ApiConexionError,
    ApiDatosInvalidosError,
    ApiHttpError,
    ApiTimeoutError,
)

log = logging.getLogger(__name__)  # Logger identificado con este módulo


def crear_sesion() -> requests.Session:  # Prepara una única sesión reutilizable con reintentos
    sesion = requests.Session()  # Crea la sesión HTTP compartida
    sesion.headers.update(  # Define cabeceras estándar para todas las consultas
        {
            "Accept": "application/json",  # Indica que esperamos respuestas JSON
            "User-Agent": "EcoTechSolutionsApp/1.0",  # Identifica nuestra app ante el servidor
        }
    )

    # Reintenta hasta 3 veces si el servidor externo está saturado (429) o falla (5xx)
    politica_reintentos = Retry(
        total=3,  # Máximo 3 reintentos por consulta
        backoff_factor=0.5,  # Espera progresiva (0.5s, 1s, 2s)
        status_forcelist=(429, 500, 502, 503, 504),  # Códigos HTTP que disparan reintento
        allowed_methods=("GET",),  # Solo reintenta peticiones GET
        respect_retry_after_header=True,  # Respeta el tiempo de espera si devuelve 429
        raise_on_status=False,  # Deja que nuestro código evalúe el status_code abajo
    )
    adaptador = HTTPAdapter(max_retries=politica_reintentos)  # Crea el adaptador con la política
    sesion.mount("https://", adaptador)  # Aplica la política a HTTPS
    sesion.mount("http://", adaptador)  # Aplica la política a HTTP
    return sesion  # Devuelve la sesión lista


SESION = crear_sesion()  # Instancia única de sesión para todo el programa
TIMEOUT = (3.05, Settings.REQUEST_TIMEOUT)  # (segundos para conectar, segundos para leer datos)


def obtener_json(url: str, params: dict | None = None) -> dict:  # Ejecuta GET y valida respuesta
    try:  # Atrapa fallos de transporte o tiempo de espera
        resp = SESION.get(url, params=params, timeout=TIMEOUT)  # Envía petición GET con timeout
    except requests.exceptions.Timeout as e:  # Si el servidor tardó más de lo permitido
        log.warning("Timeout en %s: %s", url, e)  # Registra advertencia en el log
        raise ApiTimeoutError("El servicio externo tardó demasiado en responder.") from e
    except requests.exceptions.ConnectionError as e:  # Si no hay internet o DNS falla
        log.warning("Sin conexión hacia %s: %s", url, e)  # Registra advertencia de red
        raise ApiConexionError("No hay conexión con el servicio externo.") from e
    except requests.exceptions.RequestException as e:  # Cualquier otro error de requests
        log.error("Error de red en %s: %s", url, e)  # Registra error en el log
        raise ApiConexionError("Error de comunicación con el servicio externo.") from e

    # Clasifica explícitamente cada grupo de códigos HTTP
    if resp.status_code in (400, 404):  # Solicitud inválida o recurso no encontrado
        log.info("HTTP %s en %s", resp.status_code, url)
        raise ApiHttpError(resp.status_code, "La consulta no es válida o el recurso no existe.")
    if resp.status_code in (401, 403):  # Acceso denegado por la API
        log.error("HTTP %s (acceso denegado) en %s", resp.status_code, url)
        raise ApiHttpError(resp.status_code, "Acceso denegado por el servicio externo.")
    if resp.status_code == 429 or resp.status_code >= 500:  # Saturación o caída del servidor externo
        log.warning("HTTP %s (servicio no disponible) en %s", resp.status_code, url)
        raise ApiHttpError(resp.status_code, "El servicio externo no está disponible por ahora.")
    if resp.status_code != 200:  # Cualquier otro código inesperado distinto de éxito
        log.warning("HTTP inesperado %s en %s", resp.status_code, url)
        raise ApiHttpError(resp.status_code, "Respuesta inesperada del servicio externo.")

    try:  # Intenta convertir el cuerpo recibido a diccionario Python
        datos = resp.json()  # Parsea el JSON
    except (requests.exceptions.JSONDecodeError, ValueError) as e:  # Si devolvió HTML o texto roto
        log.error("Respuesta no JSON desde %s: %s", url, e)
        raise ApiDatosInvalidosError("La respuesta del servicio no tiene formato JSON válido.") from e

    if not isinstance(datos, dict):  # Verifica que la raíz del JSON sea un objeto
        raise ApiDatosInvalidosError("Estructura JSON inesperada del servicio externo.")
    return datos  # Devuelve el diccionario listo para los servicios