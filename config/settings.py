import os  # Permite leer variables de entorno del sistema operativo
from pathlib import Path  # Construye rutas absolutas multiplataforma sin barras fijas
from dotenv import load_dotenv  # Carga variables desde el archivo .env al entorno de ejecución

# Calcula la ruta del archivo .env en la raíz del proyecto (subiendo dos niveles desde config/)
ruta_env = Path(__file__).resolve().parent.parent / ".env"  # Ruta completa hacia .env
load_dotenv(dotenv_path=ruta_env)  # Carga las variables del .env en memoria


def _requerida(nombre: str) -> str:  # Exige que una variable obligatoria exista en .env
    valor = os.getenv(nombre)  # Busca la variable por su nombre en el entorno
    if not valor or not valor.strip():  # Si falta o está en blanco, frena el arranque
        raise RuntimeError(  # Lanza error claro indicando cómo solucionar la configuración
            f"Falta la variable obligatoria '{nombre}'. Copia .env.example a .env y complétala."
        )
    return valor.strip()  # Devuelve el valor limpio sin espacios sobrantes


class Settings:  # Centraliza todas las configuraciones globales de EcoTech Solutions
    # URLs de las APIs externas (obligatorias en .env, sin valores inventados)
    GEO_API_URL: str = _requerida("GEO_API_URL")  # Endpoint de geocodificación de Open-Meteo
    WEATHER_API_URL: str = _requerida("WEATHER_API_URL")  # Endpoint de pronóstico actual de Open-Meteo
    CURRENCY_API_URL: str = _requerida("CURRENCY_API_URL")  # Endpoint de divisas Frankfurter API v2

    # Parámetros operativos de red y políticas de seguridad
    REQUEST_TIMEOUT: float = float(os.getenv("REQUEST_TIMEOUT", "5"))  # Segundos máximos de espera HTTP
    ENABLE_OFFLINE_FALLBACK: bool = os.getenv("ENABLE_OFFLINE_FALLBACK", "True").lower() in ("true", "1", "yes")  # Activa modo respaldo
    MAX_LOGIN_ATTEMPTS: int = int(os.getenv("MAX_LOGIN_ATTEMPTS", "3"))  # Intentos antes de bloquear cuenta
    LOCKOUT_MINUTES: int = int(os.getenv("LOCKOUT_MINUTES", "5"))  # Minutos de bloqueo persistente en BD

    # Nombre sugerido para el administrador inicial (la contraseña nunca se guarda en código ni .env)
    ADMIN_INITIAL_USER: str = os.getenv("ADMIN_INITIAL_USER", "admin")  # Usuario por defecto al iniciar BD vacía