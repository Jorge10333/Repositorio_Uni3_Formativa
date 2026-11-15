import logging  # Módulo estándar para bitácoras técnicas
from logging.handlers import RotatingFileHandler  # Limita el tamaño del archivo de log
from pathlib import Path  # Construye rutas seguras en cualquier sistema operativo


def configurar_logging() -> None:  # Configura el registro técnico en logs/ecotech.log
    carpeta_logs = Path(__file__).resolve().parent.parent / "logs"  # Apunta a logs/ en la raíz
    carpeta_logs.mkdir(exist_ok=True)  # Crea la carpeta logs/ si todavía no existe
    archivo_log = carpeta_logs / "ecotech.log"  # Ruta final del archivo de bitácora

    # Corta el archivo al llegar a 1 MB y conserva hasta 3 respaldos antiguos
    manejador_archivo = RotatingFileHandler(
        archivo_log, maxBytes=1_048_576, backupCount=3, encoding="utf-8"  # Soporta tildes y ñ
    )
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",  # Estructura de cada línea
        datefmt="%Y-%m-%d %H:%M:%S",  # Formato de fecha y hora legible
    )
    manejador_archivo.setFormatter(formato)  # Aplica el formato al archivo

    logger_raiz = logging.getLogger()  # Obtiene el logger principal de la aplicación
    logger_raiz.setLevel(logging.INFO)  # Registra eventos desde nivel INFO hacia arriba
    if not logger_raiz.handlers:  # Evita duplicar salidas si se llama más de una vez
        logger_raiz.addHandler(manejador_archivo)  # Conecta el archivo al logger principal