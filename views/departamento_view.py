from views.utils import leer_numero, confirmar
from models.departamento import Departamento

class DepartamentoView:
    """
    Vista encargada de las pantallas del módulo Departamento.
    """
    @staticmethod
    def mostrar_menu() -> int:
        print("\n" + "-"*30)
        print(" GESTIÓN DE DEPARTAMENTOS")
        print("-"*30)
        print("1.- Agregar departamento")
        print("2.- Editar departamento")
        print("3.- Eliminar departamento")
        print("4.- Imprimir un departamento")
        print("5.- Imprimir todos los departamentos")
        print("0.- Volver al menú principal")
        print("-"*30)
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def formulario_nuevo_departamento() -> dict:
        # Recoge la información enviada por consola para crear un departamento
        print("\n--- Agregar Nuevo Departamento ---")
        nombre = input("Ingrese el nombre del departamento: ")
        gerente_input = input("ID del Gerente Asignado (Enter si no aplica): ").strip()
        id_gerente = int(gerente_input) if gerente_input.isdigit() else None
        
        return {
            "nombre": nombre,
            "id_gerente": id_gerente
        }

    @staticmethod
    def solicitar_id() -> int:
        return leer_numero("Ingrese el ID del departamento: ")

    @staticmethod
    def mostrar_departamento(departamento: Departamento) -> None:
        print("\n--- Datos del Departamento ---")
        print(departamento)
        print("-" * 30)

    @staticmethod
    def mostrar_lista_departamentos(departamentos: list[Departamento]) -> None:
        print("\n--- Lista de Departamentos ---")
        if not departamentos:
            print("No hay departamentos registrados.")
        else:
            for d in departamentos:
                print(d)
        print("-" * 30)

    @staticmethod
    def formulario_editar_departamento(departamento: Departamento) -> dict:
        # Muestra datos actuales y mantiene los valores previos si la consola recibe Enter
        print(f"\n--- Editando Departamento [ID: {departamento.id_departamento}] ---")
        print("Deje en blanco si no desea modificar el campo.")
        
        nuevo_nombre = input(f"Nombre actual ({departamento.nombre}): ")
        if not nuevo_nombre.strip():
            nuevo_nombre = departamento.nombre
            
        gerente_actual_str = departamento.id_gerente if departamento.id_gerente is not None else "Ninguno"
        nuevo_gerente_input = input(f"ID Gerente actual ({gerente_actual_str}): ").strip()
        
        if not nuevo_gerente_input:
            nuevo_id_gerente = departamento.id_gerente
        else:
            nuevo_id_gerente = int(nuevo_gerente_input) if nuevo_gerente_input.isdigit() else None

        return {
            "id_departamento": departamento.id_departamento,
            "nombre": nuevo_nombre,
            "id_gerente": nuevo_id_gerente
        }

    @staticmethod
    def confirmar_eliminacion(nombre: str) -> bool:
        return confirmar(f"¿Está seguro que desea eliminar el departamento '{nombre}'?")

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"[DEPARTAMENTOS] {mensaje}")