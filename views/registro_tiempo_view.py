# --- Vista de Registro de Tiempo ---
from views.utils import leer_numero, leer_float
from models.registro_tiempo import RegistroTiempo

class RegistroTiempoView:
    @staticmethod
    def mostrar_menu() -> int:
        print("\n" + "-"*30)
        print(" REGISTRO DE TIEMPO / HORAS")
        print("-"*30)
        print("1.- Registrar horas trabajadas")
        print("2.- Ver horas por ID de empleado")
        print("3.- Eliminar un registro de tiempo")
        print("0.- Volver al menú principal")
        print("-"*30)
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def formulario_nuevo_registro() -> dict:
        print("\n--- Registrar Horas Trabajadas ---")
        fecha = input("Fecha (YYYY-MM-DD): ")
        horas = leer_float("Cantidad de horas trabajadas: ")
        descripcion = input("Descripción de las tareas realizadas: ")
        id_empleado = leer_numero("ID del Empleado: ")
        id_proyecto = leer_numero("ID del Proyecto: ")

        return {
            "fecha": fecha,
            "cantidad_hora_trabajada": horas,
            "descripcion_tarea_realizada": descripcion,
            "id_empleado": id_empleado,
            "id_proyecto": id_proyecto
        }

    @staticmethod
    def solicitar_id_registro() -> int:
        return leer_numero("Ingrese el ID del registro de tiempo: ")

    @staticmethod
    def solicitar_id_empleado() -> int:
        return leer_numero("Ingrese el ID del empleado a consultar: ")

    @staticmethod
    def mostrar_lista_registros(registros: list[RegistroTiempo]) -> None:
        print("\n--- Horas Registradas ---")
        if not registros:
            print("No hay registros de tiempo para este empleado.")
        else:
            for r in registros:
                print(r)
        print("-" * 30)

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"[TIEMPO] {mensaje}")