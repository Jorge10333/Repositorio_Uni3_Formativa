import getpass  # Importa getpass para leer contraseñas en consola sin mostrar los caracteres en pantalla
from views.utils import leer_numero, confirmar  # Importa funciones auxiliares de validación de entradas
from models.usuario import Usuario  # Importa el modelo Usuario para tipado


class AuthView:  # Define la vista de consola para inicio de sesión y gestión de cuentas
    """
    Vista de consola para el Inicio de Sesión y Gestión de Usuarios.
    """

    @staticmethod  # Muestra el encabezado del formulario de inicio de sesión
    def mostrar_banner_login(intento_actual: int, max_intentos: int) -> None:
        print("\n" + "=" * 58)  # Imprime línea separadora superior
        print("   ECOTECH SOLUTIONS - INICIO DE SESIÓN SEGURO (SHA-256)")  # Título del sistema
        print("=" * 58)  # Imprime línea separadora inferior
        print(f"Intento {intento_actual} de {max_intentos} (Por defecto: admin / admin1234)")  # Muestra intentos
        print("-" * 58)

    @staticmethod  # Solicita usuario y contraseña al operador
    def solicitar_credenciales() -> dict:
        nombre_usuario = input("Usuario    : ").strip()  # Lee el nombre de usuario y quita espacios
        clave = getpass.getpass("Contraseña : ").strip()  # Lee la contraseña oculta por seguridad
        return {  # Retorna ambos datos empaquetados en un diccionario
            "nombre_usuario": nombre_usuario,
            "clave": clave
        }

    @staticmethod  # Muestra mensaje de bienvenida tras superar el login
    def mostrar_bienvenida(usuario: Usuario) -> None:
        print("\n" + "*" * 58)
        print(f"  [ACCESO CONCEDIDO] Bienvenido/a, {usuario.nombre_usuario}")  # Muestra el usuario autenticado
        print(f"  Rol: {usuario.rol} | Empleado ID asociado: {usuario.id_empleado or 'Ninguno'}")  # Muestra rol
        print("*" * 58)

    @staticmethod  # Muestra el submenú de administración de usuarios
    def mostrar_menu_usuarios() -> int:
        print("\n" + "-" * 48)
        print("   GESTIÓN DE USUARIOS Y CREDENCIALES")
        print("-" * 48)
        print("1.- Registrar nuevo usuario (Encriptar clave)")  # Opción para crear cuenta con SHA-256
        print("2.- Listar usuarios y verificar hashes SHA-256")  # Opción para auditar cuentas en BD
        print("3.- Eliminar usuario")  # Opción para borrar cuentas
        print("0.- Volver al menú principal")  # Opción de retorno
        print("-" * 48)
        return leer_numero("Seleccione una opción: ")  # Lee y valida que la opción sea un número entero

    @staticmethod  # Pide los datos necesarios para crear una nueva cuenta de usuario
    def formulario_nuevo_usuario() -> dict:
        print("\n--- Registrar Nuevo Usuario ---")
        nombre_usuario = input("Ingrese nombre de usuario (mín. 3 caracteres, sin espacios): ").strip()
        clave = getpass.getpass("Ingrese contraseña (mín. 4 caracteres, se encriptará con SHA-256): ").strip()
        confirmacion = getpass.getpass("Confirme la contraseña: ").strip()  # Pide repetir la clave para evitar errores

        print("Roles disponibles: 1.- Administrador, 2.- Gerente, 3.- Empleado, 4.- Operador")
        opcion_rol = leer_numero("Seleccione un rol (1-4): ")  # Pide elegir el rol por número
        mapa_roles = {1: "Administrador", 2: "Gerente", 3: "Empleado", 4: "Operador"}  # Diccionario de mapeo
        rol = mapa_roles.get(opcion_rol, "")  # Obtiene el nombre del rol o cadena vacía si eligió otro número

        emp_raw = input("ID de empleado asociado (opcional, presione Enter para omitir): ").strip()  # ID opcional
        id_empleado = int(emp_raw) if emp_raw.isdigit() else None  # Convierte a entero solo si ingresó dígitos

        return {  # Retorna todos los campos capturados al controlador
            "nombre_usuario": nombre_usuario,
            "clave": clave,
            "confirmacion": confirmacion,
            "rol": rol,
            "id_empleado": id_empleado
        }

    @staticmethod  # Imprime en pantalla la lista de usuarios registrados
    def mostrar_lista_usuarios(usuarios: list[Usuario]) -> None:
        print("\n--- Lista de Usuarios Registrados (Credenciales Encriptadas) ---")
        if not usuarios:  # Verifica si la lista está vacía
            print("No hay usuarios registrados.")
        else:
            for u in usuarios:  # Recorre cada usuario e imprime su método __str__
                print(u)
        print("-" * 68)

    @staticmethod  # Solicita el ID numérico del usuario que se desea eliminar
    def solicitar_id_usuario() -> int:
        return leer_numero("Ingrese el ID del usuario a eliminar: ")

    @staticmethod  # Pide confirmación explícita ('si'/'no') antes de borrar un usuario
    def confirmar_eliminacion(nombre_usuario: str) -> bool:
        return confirmar(f"¿Está seguro que desea eliminar al usuario '{nombre_usuario}'?")

    @staticmethod  # Muestra mensajes informativos del módulo de autenticación
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"\n[AUTENTICACIÓN] {mensaje}")

    @staticmethod  # Muestra mensajes de error controlados del módulo de autenticación
    def mostrar_error(error: str) -> None:
        print(f"\n[ERROR DE CREDENCIALES] {error}")