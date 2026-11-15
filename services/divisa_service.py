import math  # Valida que la tasa recibida sea un número finito
import re  # Valida códigos de moneda ISO 4217 y formato de fecha
from config.settings import Settings  # Lee la URL de Frankfurter API y modo contingencia
from exceptions import ApiDatosInvalidosError, ValidacionError  # Excepciones propias de dominio y API
from services.http_client import obtener_json  # Cliente HTTP centralizado con reintentos


class DivisaService:  # Consulta tipos de cambio en Frankfurter API y valida países/monedas
    # Tasas referenciales de respaldo para consultas rápidas sin conexión
    TASAS_CONTINGENCIA: dict[str, float] = {
        "USD_CLP": 950.00,
        "USD_EUR": 0.92,
        "USD_BRL": 5.70,
        "USD_MXN": 20.10,
        "USD_COP": 4350.00,
        "USD_PEN": 3.75,
        "EUR_CLP": 1030.00,
    }

    # Catálogo de países donde EcoTech opera proyectos y su moneda oficial asociada
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

    @staticmethod
    def sanitizar_moneda(codigo: str) -> str:  # Exige un código ISO de exactamente 3 letras
        if not isinstance(codigo, str) or not codigo.strip():  # Rechaza entradas vacías
            raise ValidacionError("El código de moneda no puede estar vacío.")
        limpio = codigo.strip().upper()  # Normaliza a mayúsculas (ej. "clp" -> "CLP")
        if not re.fullmatch(r"[A-Z]{3}", limpio):  # Solo permite 3 letras A-Z sin números ni símbolos
            raise ValidacionError(f"Código de moneda '{codigo}' inválido. Use 3 letras ISO (ej. USD, CLP).")
        return limpio  # Devuelve código limpio

    @classmethod
    def validar_pais(cls, pais: str) -> str:  # Verifica que el país exista en el catálogo operativo
        if not isinstance(pais, str) or not pais.strip():  # Rechaza textos vacíos
            raise ValidacionError("Debe indicar el país del proyecto.")
        limpio = pais.strip()  # Quita espacios extremos
        if limpio.lower() not in cls.PAISES_MONEDA:  # Impide guardar países inventados o fuera de catálogo
            disponibles = ", ".join(sorted({p.title() for p in cls.PAISES_MONEDA}))
            raise ValidacionError(f"País no soportado en catálogo. Opciones: {disponibles}.")
        return limpio.title()  # Devuelve el nombre capitalizado

    @classmethod
    def sugerir_moneda_por_pais(cls, pais: str) -> str | None:  # Sugiere moneda oficial según el país ingresado
        if not isinstance(pais, str) or not pais.strip():
            return None
        return cls.PAISES_MONEDA.get(pais.strip().lower())  # Busca en minúsculas en el catálogo

    @classmethod
    def obtener_tasa_cambio(cls, moneda_origen: str, moneda_destino: str) -> tuple[float, str]:
        origen = cls.sanitizar_moneda(moneda_origen)  # Valida moneda base
        destino = cls.sanitizar_moneda(moneda_destino)  # Valida moneda destino

        if origen == destino:  # Evita consultar conversión entre la misma moneda
            raise ValidacionError("La moneda de origen y destino deben ser distintas.")

        # Construye la ruta de Frankfurter API v2 (ej. https://api.frankfurter.dev/v2/rate/usd/clp)
        url = f"{Settings.CURRENCY_API_URL.rstrip('/')}/rate/{origen.lower()}/{destino.lower()}"
        datos = obtener_json(url)  # Ejecuta la petición HTTP validando códigos y JSON

        tasa = datos.get("rate")  # Extrae el valor numérico de la tasa
        fecha_tasa = datos.get("date")  # Extrae la fecha oficial publicada por el banco central
        if not isinstance(tasa, (int, float)) or isinstance(tasa, bool) or not math.isfinite(tasa) or float(tasa) <= 0:
            raise ApiDatosInvalidosError("La API no entregó una tasa de cambio numérica válida.")
        if not isinstance(fecha_tasa, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", fecha_tasa):
            raise ApiDatosInvalidosError("La API no entregó una fecha válida para la tasa.")

        return (float(tasa), fecha_tasa)  # Retorna tupla (tasa_numérica, fecha_oficial)

    @classmethod
    def obtener_tasa_respaldo(cls, moneda_origen: str, moneda_destino: str) -> float | None:
        if not Settings.ENABLE_OFFLINE_FALLBACK:  # Verifica si el respaldo local está habilitado
            return None
        origen = cls.sanitizar_moneda(moneda_origen)
        destino = cls.sanitizar_moneda(moneda_destino)

        directa = f"{origen}_{destino}"  # Busca par directo (ej. USD_CLP)
        inversa = f"{destino}_{origen}"  # Busca par inverso (ej. CLP_USD)
        if directa in cls.TASAS_CONTINGENCIA:
            return cls.TASAS_CONTINGENCIA[directa]  # Devuelve tasa directa referencial
        if inversa in cls.TASAS_CONTINGENCIA:
            return round(1.0 / cls.TASAS_CONTINGENCIA[inversa], 6)  # Calcula tasa inversa
        return None  # Si no existe en respaldo, retorna None (sin inventar fecha de hoy)

    @staticmethod
    def probar_conectividad() -> tuple[bool, str]:  # Consulta liviana para verificar disponibilidad
        url = f"{Settings.CURRENCY_API_URL.rstrip('/')}/rate/usd/eur"
        obtener_json(url)  # Si responde HTTP 200 con JSON válido, la API está operativa
        return (True, "Conexión operativa con Frankfurter API.")