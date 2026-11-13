import re  # Importa expresiones regulares para validar el nombre de la ciudad antes de enviarlo por red

try:  # Intenta importar la librería requests para hacer peticiones HTTP
    import requests  # Librería estándar para consumir APIs REST
    REQUESTS_AVAILABLE = True  # Marca que requests está disponible
except ImportError:  # Si requests no está instalado en el entorno
    requests = None  # Asigna None para evitar errores de nombre
    REQUESTS_AVAILABLE = False  # Marca que requests no está disponible

from config.settings import Settings  # Importa URLs y tiempos de espera desde Settings
from models.reporte_clima import ReporteClima  # Importa el modelo de dominio ReporteClima


class ClimaService:  # Define la capa de servicio que encapsula la comunicación con Open-Meteo
    """
    Servicio encargado de consumir la API pública de Open-Meteo (Geolocalización + Clima).
    """

    # Catálogo local de contingencia por si se cae internet durante las pruebas o en terreno
    DATOS_CONTINGENCIA = {
        "santiago": ReporteClima("Santiago", 21.5, "Chile", 12.0),
        "concepcion": ReporteClima("Concepción", 16.2, "Chile", 18.5),
        "valparaiso": ReporteClima("Valparaíso", 18.0, "Chile", 15.0),
        "antofagasta": ReporteClima("Antofagasta", 20.4, "Chile", 14.2),
        "temuco": ReporteClima("Temuco", 14.8, "Chile", 10.5),
    }

    @staticmethod  # Método estático que limpia y valida la ciudad ingresada por el usuario
    def sanitizar_ciudad(ciudad: str) -> str:
        if not ciudad or not isinstance(ciudad, str):  # Verifica que la entrada sea un texto no vacío
            raise ValueError("El nombre de la ciudad debe ser un texto válido.")  # Rechaza entradas nulas o vacías

        limpia = ciudad.strip()  # Elimina espacios sobrantes al inicio y al final
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚáéíóúÑñ\s-]{2,50}", limpia):  # Permite solo letras, tildes, espacios y guiones
            raise ValueError("Ciudad inválida. Use solo letras y espacios (2 a 50 caracteres).")  # Bloquea símbolos/números

        return limpia  # Retorna la ciudad validada

    @classmethod  # Método de clase que ejecuta la consulta completa a las dos APIs de Open-Meteo
    def consultar_clima(cls, ciudad: str) -> tuple[ReporteClima | None, str]:
        ciudad_segura = cls.sanitizar_ciudad(ciudad)  # Valida la ciudad antes de abrir conexiones de red

        if not REQUESTS_AVAILABLE:  # Si falta la librería requests, activa el modo contingencia
            return cls._manejar_contingencia(
                ciudad_segura,
                "Librería 'requests' no instalada en el entorno."
            )

        headers = {  # Define cabeceras HTTP estándar para identificar nuestra aplicación
            "Accept": "application/json",  # Solicita respuesta en formato JSON
            "User-Agent": "EcoTechSolutionsApp/1.0"  # Identifica el cliente HTTP
        }

        try:  # Envuelve todas las peticiones HTTP para capturar cortes de red, timeouts o respuestas inválidas
            # 1. Primera petición HTTP: busca las coordenadas (latitud y longitud) de la ciudad
            resp_geo = requests.get(
                Settings.GEO_API_URL,  # URL de geocodificación tomada desde Settings
                headers=headers,  # Envía las cabeceras configuradas
                params={"name": ciudad_segura, "count": 1, "language": "es"},  # Parámetros de búsqueda segura
                timeout=Settings.REQUEST_TIMEOUT  # Tiempo límite explícito para evitar que el programa se congele
            )

            if resp_geo.status_code != 200:  # Verifica que el servidor respondió con código HTTP 200 OK
                return (None, f"Servicio de geolocalización no disponible (HTTP {resp_geo.status_code}).")

            geo_data = resp_geo.json()  # Convierte la respuesta JSON a un diccionario de Python
            resultados = geo_data.get("results", [])  # Extrae la lista de coincidencias geográficas
            if not resultados:  # Si la lista está vacía, la ciudad no existe en Open-Meteo
                return (None, f"No se encontró la ciudad '{ciudad_segura}' en el servicio externo.")

            lugar = resultados[0]  # Toma el primer resultado encontrado

            # 2. Segunda petición HTTP: consulta el clima actual usando la latitud y longitud obtenidas
            resp_clima = requests.get(
                Settings.WEATHER_API_URL,  # URL del pronóstico meteorológico tomada desde Settings
                headers=headers,  # Envía las cabeceras
                params={
                    "latitude": lugar["latitude"],    # Latitud obtenida en la primera consulta
                    "longitude": lugar["longitude"],  # Longitud obtenida en la primera consulta
                    "current_weather": True           # Solicita únicamente las condiciones actuales
                },
                timeout=Settings.REQUEST_TIMEOUT  # Tiempo máximo de espera en segundos
            )

            if resp_clima.status_code != 200:  # Valida que la segunda respuesta HTTP también sea 200 OK
                return (None, f"Servicio de clima no disponible (HTTP {resp_clima.status_code}).")

            clima_data = resp_clima.json()  # Deserializa el JSON del pronóstico
            actual = clima_data.get("current_weather")  # Extrae el bloque de clima actual
            if not actual:  # Verifica que el bloque exista en la respuesta
                return (None, "La API no entregó datos meteorológicos actuales para esta ubicación.")

            # Construye el objeto ReporteClima con los datos limpios obtenidos de internet
            reporte = ReporteClima(
                ciudad=lugar.get("name", ciudad_segura),       # Nombre oficial devuelto por la API
                pais=lugar.get("country", "No especificado"),  # País devuelto por la API
                temperatura=actual["temperature"],             # Temperatura actual en °C
                velocidad_viento=actual.get("windspeed", 0.0)  # Velocidad del viento en km/h
            )
            return (reporte, f"Consulta meteorológica exitosa para {reporte.ciudad}, {reporte.pais}.")

        except requests.exceptions.Timeout:  # Captura el error si el servidor tarda más de REQUEST_TIMEOUT segundos
            return cls._manejar_contingencia(
                ciudad_segura,
                f"El servicio tardó más de {Settings.REQUEST_TIMEOUT}s en responder (Timeout)."
            )
        except requests.exceptions.ConnectionError:  # Captura el error si no hay internet o el servidor cayó
            return cls._manejar_contingencia(
                ciudad_segura,
                "No hay conexión a internet o el servidor de Open-Meteo está inaccesible."
            )
        except (requests.exceptions.RequestException, KeyError, ValueError) as e:  # Captura otros errores HTTP o JSON
            return cls._manejar_contingencia(ciudad_segura, f"Error al procesar respuesta externa: {e}")

    @classmethod  # Método interno que busca datos locales de respaldo cuando falla la conexión externa
    def _manejar_contingencia(cls, ciudad: str, causa_error: str) -> tuple[ReporteClima | None, str]:
        if not Settings.ENABLE_OFFLINE_FALLBACK:  # Verifica si el modo respaldo está habilitado en .env
            return (None, f"{causa_error} (Modo offline deshabilitado).")

        # Normaliza minúsculas y quita tildes para buscar en el diccionario local
        clave = (
            ciudad.lower()
            .replace("á", "a").replace("é", "e").replace("í", "i")
            .replace("ó", "o").replace("ú", "u")
        )
        respaldo = cls.DATOS_CONTINGENCIA.get(clave)  # Busca la ciudad en el catálogo local
        if respaldo:  # Si existe respaldo para esa ciudad
            copia = ReporteClima(  # Crea una copia nueva con la fecha/hora actual
                ciudad=respaldo.ciudad,
                pais=respaldo.pais,
                temperatura=respaldo.temperatura,
                velocidad_viento=respaldo.velocidad_viento
            )
            return (copia, f"[MODO CONTINGENCIA] {causa_error} Se cargó registro local de respaldo.")

        return (None, f"[OFFLINE] {causa_error} No hay datos locales de respaldo para '{ciudad}'.")

    @classmethod  # Método de diagnóstico para verificar si hay conexión activa con Open-Meteo
    def probar_conectividad(cls) -> tuple[bool, str]:
        if not REQUESTS_AVAILABLE:  # Comprueba si requests está instalado
            return (False, "Librería 'requests' no instalada. Ejecute 'pip install requests'.")

        try:  # Envía una petición ligera de prueba
            resp = requests.get(
                Settings.GEO_API_URL,
                params={"name": "Santiago", "count": 1},
                timeout=Settings.REQUEST_TIMEOUT
            )
            if resp.status_code == 200:  # Si responde 200 OK, hay conexión operativa
                return (True, f"Conexión exitosa con Open-Meteo (HTTP {resp.status_code}).")
            return (False, f"El servidor respondió con código HTTP {resp.status_code}.")
        except requests.exceptions.Timeout:
            return (False, "Timeout al contactar el servidor meteorológico.")
        except requests.exceptions.ConnectionError:
            return (False, "Sin conexión de red hacia Open-Meteo.")
        except Exception as e:
            return (False, f"Error de red: {e}")