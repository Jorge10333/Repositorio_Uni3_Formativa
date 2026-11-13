from views.utils import leer_numero, confirmar  # Importa utilidades de lectura numérica y confirmación
from models.reporte_clima import ReporteClima  # Importa el modelo ReporteClima


class ClimaView:  # Define la vista de consola para el módulo de consumo de API meteorológica
    """
    Vista de consola para el módulo de Monitoreo Climático (Open-Meteo API).
    """

    @staticmethod  # Muestra las opciones del módulo de clima
    def mostrar_menu() -> int:
        print("\n" + "=" * 54)
        print("     MÓDULO DE CLIMA Y PROYECTOS EN TERRENO (API)")
        print("=" * 54)
        print("1.- Consultar Clima Actual por Ciudad (API Externa)")
        print("2.- Consultar y Guardar Reporte Climático en BD")
        print("3.- Ver Historial de Reportes Climáticos Guardados")
        print("4.- Ver Reportes Climáticos de un Proyecto")
        print("5.- Diagnosticar Conexión con API Open-Meteo")
        print("0.- Volver al Menú Principal")
        print("=" * 54)
        return leer_numero("Seleccione una opción: ")  # Valida entrada entera

    @staticmethod  # Solicita al usuario el nombre de la ciudad a consultar
    def pedir_ciudad() -> str:
        print("\n--- CONSULTA METEOROLÓGICA (OPEN-METEO) ---")
        return input("Ingrese el nombre de la ciudad (ej. 'Concepcion', 'Santiago'): ").strip()

    @staticmethod  # Imprime en consola los datos meteorológicos recibidos de la API
    def mostrar_reporte_actual(reporte: ReporteClima) -> None:
        print("\n" + "-" * 48)
        print(f"  Ciudad           : {reporte.ciudad} ({reporte.pais})")
        print(f"  Temperatura      : {reporte.temperatura:.1f} °C")
        print(f"  Velocidad Viento : {reporte.velocidad_viento:.1f} km/h")
        print(f"  Fecha Consulta   : {reporte.fecha_consulta}")
        print("-" * 48)

    @staticmethod  # Solicita opcionalmente el ID de un proyecto para vincular el reporte
    def pedir_id_proyecto_opcional() -> int | None:
        resp = input("ID del proyecto a asociar (presione Enter para guardar sin proyecto): ").strip()
        if not resp:  # Si el usuario presionó Enter sin escribir nada
            return None  # Guarda sin proyecto asociado
        if resp.isdigit():  # Si escribió solo números
            return int(resp)  # Retorna el ID como entero
        print("ID no numérico; se guardará como consulta general sin proyecto asociado.")
        return None  # Si escribió letras, evita error y guarda sin proyecto

    @staticmethod  # Pide confirmación antes de insertar el reporte en SQLite
    def confirmar_guardado() -> bool:
        return confirmar("¿Desea guardar este reporte climático en la base de datos SQLite?")

    @staticmethod  # Pide el ID de proyecto para filtrar su historial meteorológico
    def pedir_id_proyecto_busqueda() -> int:
        return leer_numero("Ingrese el ID del proyecto a consultar: ")

    @staticmethod  # Muestra la lista de reportes guardados en la base de datos
    def mostrar_historial(reportes: list[ReporteClima]) -> None:
        if not reportes:  # Si no hay registros en SQLite
            print("\n[INFO] No hay reportes climáticos registrados.")
            return
        print(f"\n--- HISTORIAL DE REPORTES CLIMÁTICOS ({len(reportes)}) ---")
        for r in reportes:  # Imprime cada reporte formateado
            print(f"• {r}")
        print("-" * 54)

    @staticmethod  # Muestra mensajes informativos del módulo clima
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"\n[CLIMA] {mensaje}")

    @staticmethod  # Muestra mensajes de error del módulo clima
    def mostrar_error(error: str) -> None:
        print(f"\n[ERROR] {error}")