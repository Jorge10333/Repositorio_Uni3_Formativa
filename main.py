import logging  # Registra errores graves en el archivo de log sin exponer trazas en consola
from config.database import Database  # Prepara la conexión y tablas de SQLite
from config.logging_config import configurar_logging  # Inicializa logs/ecotech.log
from controllers.main_controller import MainController  # Orquesta el flujo principal
from exceptions import EcoTechError  # Atrapa errores controlados del sistema


def main() -> None:  # Punto de entrada principal del sistema
    configurar_logging()  # Activa la bitácora rotativa antes de cualquier operación
    try:
        Database().init_db()  # Crea las tablas en ecotech_solutions.db si aún no existen
        MainController().ejecutar()  # Ejecuta inicio de sesión y menús
    except (KeyboardInterrupt, EOFError):  # Cierre limpio si presionan Ctrl+C o Ctrl+Z
        print("\n[SISTEMA] Sesión finalizada por el usuario.")
    except (EcoTechError, RuntimeError) as e:  # Errores conocidos (ej. falta .env) sin traceback
        print(f"\n[ERROR] {e}")
    except Exception:  # Único respaldo genérico: guarda traza en log y avisa con mensaje seguro
        logging.getLogger(__name__).exception("Error inesperado en ejecución")
        print("\n[ERROR] Ocurrió un error inesperado. Revise logs/ecotech.log.")


if __name__ == "__main__":
    main()