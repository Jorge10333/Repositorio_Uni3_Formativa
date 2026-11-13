from views.utils import leer_numero, confirmar
from models.proyecto import Proyecto

class ProyectoView:
    @staticmethod
    def mostrar_menu() -> int:
        print("\n" + "-"*30)
        print(" GESTIÓN DE PROYECTOS")
        print("-"*30)
        print("1.- Crear proyecto")
        print("2.- Editar proyecto")
        print("3.- Asignar empleado a proyecto")
        print("4.- Desasignar empleado de proyecto")
        print("5.- Imprimir un proyecto")
        print("6.- Imprimir todos los proyectos")
        print("7.- Eliminar proyecto")
        print("0.- Volver al menú principal")
        print("-"*30)
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def formulario_nuevo_proyecto() -> dict:
        print("\n--- Crear Nuevo Proyecto ---")
        nombre = input("Nombre del Proyecto: ")
        descripcion = input("Descripción: ")
        fecha_inicio = input("Fecha de Inicio (YYYY-MM-DD): ")
        return {
            "nombre": nombre,
            "descripcion": descripcion,
            "fecha_inicio": fecha_inicio
        }

    @staticmethod
    def formulario_editar_proyecto(proyecto: Proyecto) -> dict:
        print(f"\n--- Editando Proyecto [ID: {proyecto.id_proyecto}] ---")
        print("Deje en blanco si no desea modificar el campo.")
        nuevo_nombre = input(f"Nombre actual ({proyecto.nombre}): ") or proyecto.nombre
        nueva_desc = input(f"Descripción actual ({proyecto.descripcion}): ") or proyecto.descripcion
        nueva_fecha = input(f"Fecha Inicio actual ({proyecto.fecha_inicio}): ") or proyecto.fecha_inicio
        
        return {
            "nombre": nuevo_nombre,
            "descripcion": nueva_desc,
            "fecha_inicio": nueva_fecha
        }

    @staticmethod
    def solicitar_id() -> int:
        return leer_numero("Ingrese el ID del proyecto: ")

    @staticmethod
    def solicitar_id_empleado() -> int:
        return leer_numero("Ingrese el ID del empleado: ")

    @staticmethod
    def mostrar_proyecto(proyecto: Proyecto) -> None:
        print("\n--- Datos del Proyecto ---")
        print(proyecto)
        print("-" * 30)

    @staticmethod
    def mostrar_lista_proyectos(proyectos: list[Proyecto]) -> None:
        print("\n--- Lista de Proyectos ---")
        if not proyectos:
            print("No hay proyectos registrados.")
        else:
            for p in proyectos:
                print(p)
        print("-" * 30)

    @staticmethod
    def confirmar_eliminacion(nombre: str) -> bool:
        return confirmar(f"¿Está seguro que desea eliminar el proyecto '{nombre}'?")

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"[PROYECTOS] {mensaje}")