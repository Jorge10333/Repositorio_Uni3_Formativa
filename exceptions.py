class EcoTechError(Exception):  # Error raíz para agrupar fallos propios de nuestra aplicación
    pass  # Solo identifica errores controlados del sistema


class ValidacionError(EcoTechError):  # Se lanza cuando el usuario escribe datos inválidos
    pass  # Hereda de EcoTechError


class AutenticacionError(EcoTechError):  # Se lanza cuando fallan las credenciales o hay bloqueo
    pass  # Hereda de EcoTechError


class AccesoDenegadoError(EcoTechError):  # Se lanza si entran a un menú sin sesión o sin rol autorizado
    pass  # Hereda de EcoTechError


class ApiError(EcoTechError):  # Clase padre para cualquier problema con las APIs externas
    pass  # Agrupa timeout, red, HTTP y formato JSON


class ApiTimeoutError(ApiError):  # Cuando la API externa tarda más segundos de lo permitido
    pass  # Permite activar el respaldo local ante lentitud


class ApiConexionError(ApiError):  # Cuando no hay internet o el servidor externo está caído
    pass  # Permite trabajar en modo contingencia sin que caiga el programa


class ApiDatosInvalidosError(ApiError):  # Cuando la respuesta no es JSON válido o faltan campos
    pass  # Protege al sistema de datos externos corruptos


class ApiHttpError(ApiError):  # Cuando la API responde con un código HTTP distinto de 200
    def __init__(self, estado: int, mensaje: str):  # Guarda el código HTTP y un mensaje claro
        super().__init__(mensaje)  # Pasa el mensaje legible a Exception
        self.estado = estado  # Guarda el código numérico (404, 429, 500, etc.)