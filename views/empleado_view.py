from views.utils import leer_numero, leer_float, confirmar
from models.empleado import Empleado
from models.departamento import Departamento

class EmpleadoView:
    @staticmethod
    def mostrar_menu() -> int:
        print("\n" + "-"*30)
        print(" GESTIÓN DE EMPLEADOS")
        print("-"*30)
        print("1.- Agregar empleado")
        print("2.- Editar empleado")
        print("3.- Eliminar empleado")
        print("4.- Imprimir un empleado")
        print("5.- Imprimir todos los empleados")
        print("0.- Volver al menú principal")
        print("-"*30)
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def formulario_nuevo_empleado(departamentos: list[Departamento]) -> dict:
        print("\n--- Agregar Nuevo Empleado ---")
        nombre = input("Nombre completo: ")
        direccion = input("Dirección: ")
        telefono = input("Teléfono: ")
        email = input("Email: ")
        fecha_inicio = input("Fecha de inicio (YYYY-MM-DD): ")
        salario = leer_float("Salario: ")

        print("\nDepartamentos disponibles:")
        for dep in departamentos:
            print(f" [{dep.id_departamento}] - {dep.nombre}")
        
        id_depto_input = input("Seleccione ID de Departamento (Enter para ninguno): ").strip()
        id_departamento = int(id_depto_input) if id_depto_input.isdigit() else None

        return {
            "nombre": nombre,
            "direccion": direccion,
            "telefono": telefono,
            "email": email,
            "fecha_inicio": fecha_inicio,
            "salario": salario,
            "id_departamento": id_departamento
        }

    @staticmethod
    def solicitar_id() -> int:
        return leer_numero("Ingrese el ID del empleado: ")

    @staticmethod
    def mostrar_empleado(empleado: Empleado) -> None:
        print("\n--- Datos del Empleado ---")
        print(empleado)
        print("-" * 30)

    @staticmethod
    def mostrar_lista_empleados(empleados: list[Empleado]) -> None:
        print("\n--- Lista de Empleados ---")
        if not empleados:
            print("No hay empleados registrados.")
        else:
            for e in empleados:
                print(e)
        print("-" * 30)

    @staticmethod
    def formulario_editar_empleado(empleado: Empleado, departamentos: list[Departamento]) -> dict:
        print(f"\n--- Editando Empleado [ID: {empleado.id_unico}] ---")
        print("Deje en blanco si no desea modificar el campo.")

        nuevo_nombre = input(f"Nombre actual ({empleado.nombre}): ") or empleado.nombre
        nueva_direccion = input(f"Dirección actual ({empleado.direccion}): ") or empleado.direccion
        nuevo_telefono = input(f"Teléfono actual ({empleado.telefono}): ") or empleado.telefono
        nuevo_email = input(f"Email actual ({empleado.email}): ") or empleado.email
        nueva_fecha = input(f"Fecha Inicio actual ({empleado.fecha_inicio}): ") or empleado.fecha_inicio

        # Conversión de salario resguardada
        salario_input = input(f"Salario actual ({empleado.salario}): ").strip()
        if not salario_input:
            nuevo_salario = empleado.salario
        else:
            try:
                nuevo_salario = float(salario_input)
            except ValueError:
                print("⚠️ Salario inválido ingresado. Se mantendrá el salario previo.")
                nuevo_salario = empleado.salario

        print("\nDepartamentos disponibles:")
        for dep in departamentos:
            print(f" [{dep.id_departamento}] - {dep.nombre}")
        
        depto_actual_id = empleado.departamento.id_departamento if empleado.departamento else "Ninguno"
        id_depto_input = input(f"ID Departamento actual ({depto_actual_id}): ").strip()
        
        if not id_depto_input:
            id_departamento = empleado.departamento.id_departamento if empleado.departamento else None
        else:
            id_departamento = int(id_depto_input) if id_depto_input.isdigit() else None

        return {
            "nombre": nuevo_nombre,
            "direccion": nueva_direccion,
            "telefono": nuevo_telefono,
            "email": nuevo_email,
            "fecha_inicio": nueva_fecha,
            "salario": nuevo_salario,
            "id_departamento": id_departamento
        }

    @staticmethod
    def confirmar_eliminacion(nombre: str) -> bool:
        return confirmar(f"¿Está seguro que desea eliminar al empleado '{nombre}'?")

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"[EMPLEADOS] {mensaje}")