import re  # Importa expresiones regulares para validar códigos de moneda ISO
from datetime import datetime  # Importa datetime para sellar fechas en modo contingencia

try:  # Intenta importar la librería requests para realizar peticiones HTTP
    import requests  # Librería para consumir APIs REST externas
    REQUESTS_AVAILABLE = True  # Indica que requests está disponible
except ImportError:  # Si requests no está instalado
    requests = None  # Evita error de referencia
    REQUESTS_AVAILABLE = False  # Indica que requests no está disponible

from config.settings import Settings  # Importa la URL de Frankfurter y el timeout desde Settings


class DivisaService:  # Define la capa de servicio que consume Frankfurter API
    """
    Servicio encargado de consultar indicadores económicos y tipos de cambio
    internacionales desde Frankfurter API (https://api.frankfurter.dev/v2).
    """

    # Diccionario de contingencia local por si falla internet durante una operación en terreno
    TASAS_CONTINGENCIA: dict[str, float] = {
        "USD_CLP": 950.00,   # Dólar estadounidense a Peso chileno
        "USD_EUR": 0.92,     # Dólar estadounidense a Euro
        "USD_BRL": 5.70,     # Dólar estadounidense a Real brasileño
        "USD_MXN": 20.10,    # Dólar estadounidense a Peso mexicano
        "USD_COP": 4350.00,  # Dólar estadounidense a Peso colombiano
        "USD_PEN": 3.75,     # Dólar estadounidense a Sol peruano
        "EUR_CLP": 1030.00,  # Euro a Peso chileno
    }

    # Mapa auxiliar de países comunes hacia su moneda oficial para ayudar al operador
    PAISES_MONEDA: dict[str, str] = {
        "chile": "CLP",
        "estados unidos": "USD",
        "eeuu": "USD",
        "espana": "EUR",
        "españa": "EUR",
        "alemania": "EUR",
        "brasil": "BRL",
        "mexico": "MXN",
        "méxico": "MXN",
        "colombia": "COP",
        "peru": "PEN",
        "perú": "PEN",
    }

    @staticmethod  # Valida y normaliza un código de moneda ISO de 3 letras
    def sanitizar_moneda(codigo: str) -> str:
        if not codigo or not isinstance(codigo, str):  # Verifica que sea texto no vacío
            raise ValueError("El código de moneda no puede estar vacío.")  # Lanza error de validación
        limpio = codigo.strip().upper()  # Elimina espacios y convierte a mayúsculas
        if not re.fullmatch(r"[A-Z]{3}", limpio):  # Exige exactamente 3 letras mayúsculas (ej. USD, CLP)
            raise ValueError(f"Código de moneda '{codigo}' inválido. Use 3 letras ISO (ej. USD, CLP, EUR).")
        return limpio  # Retorna el código limpio

    @classmethod  # Sugiere la moneda oficial a partir del nombre del país del proyecto
    def sugerir_moneda_por_pais(cls, pais: str) -> str | None:
        if not pais or not isinstance(pais, str):  # Verifica entrada válida
            return None  # Retorna None si está vacío
        return cls.PAISES_MONEDA.get(pais.strip().lower())  # Busca el país en minúsculas y retorna su código ISO

    @classmethod  # Consulta el tipo de cambio actual entre dos monedas en Frankfurter API v2
    def obtener_tasa_cambio(cls, moneda_origen: str, moneda_destino: str) -> tuple[float | None, str, str]:
        origen = cls.sanitizar_moneda(moneda_origen)  # Valida la moneda de origen
        destino = cls.sanitizar_moneda(moneda_destino)  # Valida la moneda de destino

        if origen == destino:  # Si ambas monedas son iguales, la tasa es exactamente 1.0 sin gastar red
            hoy = datetime.now().strftime("%Y-%m-%d")  # Obtiene fecha actual
            return (1.0, hoy, f"Moneda origen y destino idénticas ({origen}). Tasa aplicada: 1.0000.")

        if not REQUESTS_AVAILABLE:  # Si falta requests, recurre al respaldo local
            return cls._manejar_contingencia(origen, destino, "Librería 'requests' no instalada.")

        # Construye la URL del endpoint de tasa puntual de Frankfurter v2: /rate/{base}/{quote}
        url = f"{Settings.CURRENCY_API_URL.rstrip('/')}/rate/{origen.lower()}/{destino.lower()}"
        headers = {  # Cabeceras HTTP estándar
            "Accept": "application/json",  # Solicita respuesta JSON
            "User-Agent": "EcoTechSolutionsApp/1.0"  # Identifica la aplicación cliente
        }

        try:  # Envuelve la petición HTTP para capturar cortes de red, timeouts o monedas no soportadas
            respuesta = requests.get(
                url,  # Endpoint de Frankfurter v2
                headers=headers,  # Envía cabeceras
                timeout=Settings.REQUEST_TIMEOUT  # Límite explícito de espera para evitar bloqueos (Bandit B113)
            )

            if respuesta.status_code == 404:  # Si la API indica que el par de monedas no existe
                return (None, "", f"El par de monedas '{origen} -> {destino}' no está disponible en Frankfurter API.")

            if respuesta.status_code != 200:  # Si el servidor devuelve cualquier otro error HTTP
                return (None, "", f"Servicio de divisas no disponible (HTTP {respuesta.status_code}).")

            datos = respuesta.json()  # Deserializa el cuerpo JSON a diccionario Python
            tasa = datos.get("rate")  # Extrae el valor numérico del tipo de cambio
            fecha_tasa = datos.get("date", datetime.now().strftime("%Y-%m-%d"))  # Extrae la fecha oficial de la tasa

            if tasa is None or not isinstance(tasa, (int, float)):  # Verifica que el campo 'rate' sea válido
                return (None, "", "La API externa no entregó una tasa de cambio numérica válida.")

            return (
                float(tasa),
                str(fecha_tasa),
                f"Tasa oficial obtenida de Frankfurter API ({fecha_tasa}): 1 {origen} = {float(tasa):.4f} {destino}."
            )  # Retorna la tasa, su fecha y el mensaje de éxito

        except requests.exceptions.Timeout:  # Captura el error si Frankfurter tarda más de REQUEST_TIMEOUT segundos
            return cls._manejar_contingencia(
                origen,
                destino,
                f"Timeout: Frankfurter API tardó más de {Settings.REQUEST_TIMEOUT}s en responder."
            )
        except requests.exceptions.ConnectionError:  # Captura el error si no hay conexión a internet
            return cls._manejar_contingencia(
                origen,
                destino,
                "Sin conexión a internet para contactar Frankfurter API."
            )
        except (requests.exceptions.RequestException, ValueError, KeyError) as e:  # Captura otros fallos HTTP/JSON
            return cls._manejar_contingencia(origen, destino, f"Error al procesar respuesta económica: {e}")

    @classmethod  # Entrega una tasa referencial guardada localmente cuando falla internet
    def _manejar_contingencia(cls, origen: str, destino: str, causa: str) -> tuple[float | None, str, str]:
        if not Settings.ENABLE_OFFLINE_FALLBACK:  # Verifica si el respaldo offline está activo en .env
            return (None, "", f"{causa} (Modo contingencia deshabilitado).")

        clave_directa = f"{origen}_{destino}"  # Construye clave directa (ej. 'USD_CLP')
        clave_inversa = f"{destino}_{origen}"  # Construye clave inversa (ej. 'CLP_USD')
        hoy = datetime.now().strftime("%Y-%m-%d")  # Fecha actual para el registro

        if clave_directa in cls.TASAS_CONTINGENCIA:  # Busca coincidencia directa
            tasa = cls.TASAS_CONTINGENCIA[clave_directa]
            return (tasa, hoy, f"[MODO CONTINGENCIA] {causa} Se usó tasa referencial local: {tasa:.4f}.")

        if clave_inversa in cls.TASAS_CONTINGENCIA:  # Calcula la tasa inversa si existe el par al revés
            tasa = round(1.0 / cls.TASAS_CONTINGENCIA[clave_inversa], 6)
            return (tasa, hoy, f"[MODO CONTINGENCIA] {causa} Se usó tasa inversa referencial: {tasa:.6f}.")

        return (None, "", f"[OFFLINE] {causa} No hay tasa local de respaldo para {origen} -> {destino}.")

    @classmethod  # Prueba la conectividad con Frankfurter API sin afectar registros
    def probar_conectividad(cls) -> tuple[bool, str]:
        if not REQUESTS_AVAILABLE:  # Verifica si requests está instalado
            return (False, "Librería 'requests' no instalada. Ejecute 'pip install requests'.")
        try:  # Realiza una consulta liviana de prueba (USD a EUR)
            url = f"{Settings.CURRENCY_API_URL.rstrip('/')}/rate/usd/eur"
            resp = requests.get(url, timeout=Settings.REQUEST_TIMEOUT)  # Petición con timeout explícito
            if resp.status_code == 200:  # Si responde HTTP 200 OK
                return (True, f"Conexión exitosa con Frankfurter API (HTTP {resp.status_code}).")
            return (False, f"Frankfurter API respondió con código HTTP {resp.status_code}.")
        except requests.exceptions.Timeout:
            return (False, "Timeout al contactar Frankfurter API.")
        except requests.exceptions.ConnectionError:
            return (False, "Sin conexión de red hacia Frankfurter API.")
        except Exception as e:
            return (False, f"Error de red: {e}")