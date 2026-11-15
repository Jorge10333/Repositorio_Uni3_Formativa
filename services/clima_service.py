import re  # Valida el nombre de la ciudad antes de enviarlo a la API
from config.settings import Settings  # Lee las URLs configuradas y el modo contingencia
from exceptions import ApiDatosInvalidosError, ApiHttpError, ValidacionError  # Errores controlados
from models.reporte_clima import ReporteClima  # Modelo de dominio donde se empaqueta el clima
from services.http_client import obtener_json  # Cliente HTTP único con sesión, timeout y reintentos


class ClimaService:  # Administra las consultas a Open-Meteo y el respaldo local sin red
    # Diccionario de respaldo local por si se corta internet durante operaciones en terreno
    DATOS_CONTINGENCIA: dict[str, dict] = {
        "santiago": {"ciudad": "Santiago", "pais": "Chile", "temp": 21.5, "hum": 45.0, "cod": 0, "viento": 12.0},
        "concepcion": {"ciudad": "Concepción", "pais": "Chile", "temp": 16.2, "hum": 68.0, "cod": 2, "viento": 18.5},
        "valparaiso": {"ciudad": "Valparaíso", "pais": "Chile", "temp": 18.0, "hum": 72.0, "cod": 1, "viento": 15.0},
        "antofagasta": {"ciudad": "Antofagasta", "pais": "Chile", "temp": 20.4, "hum": 60.0, "cod": 0, "viento": 14.2},
        "temuco": {"ciudad": "Temuco", "pais": "Chile", "temp": 14.8, "hum": 78.0, "cod": 61, "viento": 10.5},
    }

    # Acepta letras Unicode (tildes, ñ, ü, ã como en "São Paulo" o "Chillán"), espacios simples y guiones
    REGEX_CIUDAD = re.compile(r"^[^\W\d_]+(?:[ '\-][^\W\d_]+)*$", re.UNICODE)

    @classmethod
    def sanitizar_ciudad(cls, ciudad: str) -> str:  # Limpia y valida el texto ingresado por el usuario
        if not isinstance(ciudad, str) or not ciudad.strip():  # Rechaza entradas vacías o solo espacios
            raise ValidacionError("Debe ingresar el nombre de una ciudad.")
        limpia = ciudad.strip()  # Quita espacios al inicio y al final
        if not (2 <= len(limpia) <= 60) or not cls.REGEX_CIUDAD.fullmatch(limpia):  # Exige largo y caracteres válidos
            raise ValidacionError("Ciudad inválida. Use solo letras y espacios simples (2 a 60 caracteres).")
        return limpia  # Devuelve el nombre listo para consultar

    @classmethod
    def consultar_clima(cls, ciudad: str) -> ReporteClima:  # Consulta coordenadas y clima actual en Open-Meteo
        ciudad_segura = cls.sanitizar_ciudad(ciudad)  # Filtra la entrada antes de salir a internet

        # Paso 1: Open-Meteo trabaja por coordenadas, así que primero buscamos latitud y longitud
        geo_data = obtener_json(
            Settings.GEO_API_URL,  # Endpoint de geocodificación cargado desde .env
            params={"name": ciudad_segura, "count": 1, "language": "es"},  # Parámetros seguros vía requests
        )
        resultados = geo_data.get("results")  # Extrae la lista de coincidencias encontradas
        if not isinstance(resultados, list) or not resultados:  # Si no hubo coincidencias para ese nombre
            raise ApiHttpError(404, f"No se encontró la ciudad '{ciudad_segura}' en el servicio externo.")

        lugar = resultados[0]  # Toma la primera coincidencia más relevante
        lat = lugar.get("latitude")  # Extrae la latitud geográfica
        lon = lugar.get("longitude")  # Extrae la longitud geográfica
        if not isinstance(lat, (int, float)) or not isinstance(lon, (int, float)):  # Verifica que sean números
            raise ApiDatosInvalidosError("Coordenadas inválidas recibidas desde geocodificación.")

        # Paso 2: Con esas coordenadas solicitamos temperatura, humedad, código de estado WMO y viento
        clima_data = obtener_json(
            Settings.WEATHER_API_URL,  # Endpoint de pronóstico cargado desde .env
            params={
                "latitude": lat,  # Latitud obtenida en el paso anterior
                "longitude": lon,  # Longitud obtenida en el paso anterior
                "current": "temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m",  # Variables actuales
            },
        )
        actual = clima_data.get("current")  # Extrae el bloque con las mediciones actuales
        if not isinstance(actual, dict):  # Si la respuesta no trae el bloque esperado
            raise ApiDatosInvalidosError("La API no entregó el bloque meteorológico actual.")

        try:  # Convierte cada campo y construye el objeto de dominio ReporteClima
            return ReporteClima(
                ciudad=str(lugar.get("name") or ciudad_segura),  # Nombre oficial devuelto por la API
                pais=str(lugar.get("country") or "No especificado"),  # País devuelto por la API
                temperatura=float(actual["temperature_2m"]),  # Temperatura actual en °C
                humedad=float(actual["relative_humidity_2m"]),  # Humedad relativa en %
                codigo_clima=int(actual["weather_code"]),  # Código WMO (el modelo lo traduce a texto)
                velocidad_viento=float(actual["wind_speed_10m"]),  # Velocidad del viento en km/h
                origen="API",  # Marca que el dato proviene de consulta real en vivo
            )
        except (KeyError, TypeError, ValueError) as e:  # Si falta algún campo o viene con tipo erróneo
            raise ApiDatosInvalidosError("Datos meteorológicos incompletos o inválidos.") from e

    @classmethod
    def obtener_respaldo(cls, ciudad: str) -> ReporteClima | None:  # Entrega datos locales marcados como respaldo
        if not Settings.ENABLE_OFFLINE_FALLBACK:  # Respeta si el modo contingencia fue desactivado en .env
            return None
        # Normaliza tildes y mayúsculas para buscar en el diccionario local
        clave = (
            ciudad.strip().lower()
            .replace("á", "a").replace("é", "e").replace("í", "i")
            .replace("ó", "o").replace("ú", "u")
        )
        datos = cls.DATOS_CONTINGENCIA.get(clave)  # Busca la ciudad en los datos de contingencia
        if not datos:  # Si la ciudad no está en el respaldo local
            return None
        return ReporteClima(
            ciudad=datos["ciudad"],
            pais=datos["pais"],
            temperatura=datos["temp"],
            humedad=datos["hum"],
            codigo_clima=datos["cod"],
            velocidad_viento=datos["viento"],
            origen="contingencia",  # Marca explícitamente que no es un dato en vivo
        )

    @staticmethod
    def probar_conectividad() -> tuple[bool, str]:  # Realiza una consulta mínima para diagnosticar red
        obtener_json(Settings.GEO_API_URL, params={"name": "Santiago", "count": 1})  # Prueba endpoint
        return (True, "Conexión operativa con Open-Meteo API.")  # Si no lanzó excepción, hay conexión