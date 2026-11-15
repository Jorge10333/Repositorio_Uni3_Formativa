from views.utils import leer_numero, leer_id_opcional, confirmar
from models.reporte_clima import ReporteClima


class ClimaView:  # Interfaz de consola para Monitoreo Climático en Terreno
    @staticmethod
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
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def pedir_ciudad() -> str:
        print("\n--- CONSULTA METEOROLÓGICA (OPEN-METEO) ---")
        return input("Ingrese el nombre de la ciudad (ej. 'Concepción', 'Chillán'): ").strip()

    @staticmethod
    def mostrar_reporte_actual(reporte: ReporteClima) -> None:  # Muestra métricas y recomendación operativa
        decision, detalle = reporte.evaluar_condiciones()
        print("\n" + "-" * 54)
        print(f"  Origen Dato      : {reporte.origen.upper()}")
        print(f"  Ciudad           : {reporte.ciudad} ({reporte.pais})")
        print(f"  Estado Tiempo    : {reporte.descripcion_clima}")
        print(f"  Temperatura      : {reporte.temperatura:.1f} °C")
        print(f"  Humedad Relativa : {reporte.humedad:.0f} %")
        print(f"  Velocidad Viento : {reporte.velocidad_viento:.1f} km/h")
        print(f"  Recomendación    : [{decision}] {detalle}")
        print(f"  Fecha Consulta   : {reporte.fecha_consulta}")
        print("-" * 54)

    @staticmethod
    def pedir_id_proyecto_opcional() -> int | None:
        return leer_id_opcional("ID del proyecto a asociar (Enter para guardar sin proyecto): ")

    @staticmethod
    def confirmar_guardado() -> bool:
        return confirmar("¿Desea guardar este reporte climático en la base de datos?")

    @staticmethod
    def pedir_id_proyecto_busqueda() -> int:
        return leer_numero("Ingrese el ID del proyecto a consultar: ")

    @staticmethod
    def mostrar_historial(reportes: list[ReporteClima]) -> None:
        if not reportes:
            print("\n[INFO] No hay reportes climáticos registrados.")
            return
        print(f"\n--- HISTORIAL DE REPORTES CLIMÁTICOS ({len(reportes)}) ---")
        for r in reportes:
            print(f"• {r}")
        print("-" * 54)

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"\n[CLIMA] {mensaje}")

    @staticmethod
    def mostrar_error(error: str) -> None:
        print(f"\n[ERROR] {error}")