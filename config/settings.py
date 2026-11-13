import os  # Importa el módulo del sistema operativo para leer variables de entorno
from pathlib import Path  # Importa Path para construir rutas de archivos de forma segura y multiplataforma

try:  # Intenta importar y cargar el archivo .env si python-dotenv está instalado
    from dotenv import load_dotenv  # Importa la función que carga variables desde un archivo .env
    env_path = Path(__file__).resolve().parent.parent / ".env"  # Construye la ruta completa al archivo .env en la raíz
    load_dotenv(dotenv_path=env_path)  # Carga las variables del archivo .env en el entorno de ejecución
except ImportError:  # Si la librería python-dotenv no está instalada, evita que el programa falle
    pass  # Continúa utilizando los valores por defecto definidos en la clase


class Settings:  # Define la clase central de configuración de la aplicación
    """
    Centraliza las variables de configuración del sistema EcoTech Solutions.
    """
    GEO_API_URL: str = os.getenv("GEO_API_URL", "https://geocoding-api.open-meteo.com/v1/search")  # URL de geocodificación
    WEATHER_API_URL: str = os.getenv("WEATHER_API_URL", "https://api.open-meteo.com/v1/forecast")  # URL de clima actual
    # Lee la URL de Frankfurter API v2 para obtener tasas de cambio internacionales
    CURRENCY_API_URL: str = os.getenv("CURRENCY_API_URL", "https://api.frankfurter.dev/v2")  # URL de divisas internacionales
    REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "5"))  # Límite de espera HTTP en segundos
    ENABLE_OFFLINE_FALLBACK: bool = os.getenv("ENABLE_OFFLINE_FALLBACK", "True").lower() in ("true", "1", "yes")  # Modo respaldo

    ADMIN_INITIAL_USER: str = os.getenv("ADMIN_INITIAL_USER", "admin")  # Usuario administrador inicial
    ADMIN_INITIAL_CLAVE: str = os.getenv("ADMIN_INITIAL_CLAVE", "admin1234")  # Contraseña inicial (se guarda como hash SHA-256)
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "3"))  # Máximo de intentos fallidos en login