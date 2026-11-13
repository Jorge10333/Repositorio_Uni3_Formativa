from views.utils import leer_numero  # Importa la función para leer números enteros de forma segura
from models.usuario import Usuario  # Importa el modelo Usuario para mostrar la sesión activa


class MainView:  # Define la vista del menú principal de EcoTech Solutions
    @staticmethod
    def mostrar_menu(usuario_actual: Usuario | None = None) -> int:
        print("\n" + "=" * 58)
        print("     ECOTECH SOLUTIONS - MENÚ PRINCIPAL (UNIDAD 3)")
        if usuario_actual:  # Si hay un usuario autenticado, muestra su nombre y rol en la cabecera
            print(f"     Sesión activa: {usuario_actual.nombre_usuario} ({usuario_actual.rol})")
        print("=" * 58)
        print("1.- Gestión de Empleados y Departamentos")
        print("2.- Gestión de Proyectos y Registro de Tiempo")
        print("3.- Monitoreo Climático en Terreno (Consumo API Open-Meteo)")
        print("4.- Gestión de Usuarios (Credenciales Encriptadas)")
        print("5.- Pagos Internacionales y Divisas (Frankfurter API)")
        print("9.- Cerrar Sesión (Cambiar de Usuario)")
        print("0.- Salir del Sistema")
        print("=" * 58)
        return leer_numero("Seleccione una opción: ")  # Solicita y valida la opción numérica

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"\n[SISTEMA] {mensaje}")  # Muestra mensajes generales del sistema