import getpass  # Oculta la contraseña mientras el usuario la escribe en consola
from views.utils import leer_numero, leer_id_opcional, confirmar
from models.usuario import Usuario


class AuthView:  # Interfaz de consola para inicio de sesión y gestión de cuentas
    @staticmethod
    def mostrar_banner_login(intento_actual: int, max_intentos: int) -> None:
        print("\n" + "=" * 58)
        print("   ECOTECH SOLUTIONS - INICIO DE SESIÓN SEGURO")
        print("=" * 58)
        print(f"Intento {intento_actual} de {max_intentos}")  # Sin pistas ni claves en pantalla
        print("-" * 58)

    @staticmethod
    def solicitar_credenciales() -> dict:
        nombre_usuario = input("Usuario    : ").strip()
        clave = getpass.getpass("Contraseña : ")  # No usa .strip() para respetar la clave exacta
        return {"nombre_usuario": nombre_usuario, "clave": clave}

    @staticmethod
    def mostrar_bienvenida(usuario: Usuario) -> None:
        print("\n" + "*" * 58)
        print(f"  [ACCESO CONCEDIDO] Bienvenido/a, {usuario.nombre_usuario}")
        print(f"  Rol: {usuario.rol} | Empleado ID asociado: {usuario.id_empleado or 'Ninguno'}")
        print("*" * 58)

    @staticmethod
    def mostrar_menu_usuarios() -> int:
        print("\n" + "-" * 48)
        print("   GESTIÓN DE USUARIOS Y CREDENCIALES")
        print("-" * 48)
        print("1.- Registrar nuevo usuario (Hash scrypt)")
        print("2.- Listar usuarios registrados")
        print("3.- Eliminar usuario")
        print("0.- Volver al menú principal")
        print("-" * 48)
        return leer_numero("Seleccione una opción: ")

    @staticmethod
    def formulario_nuevo_usuario() -> dict:
        print("\n--- Registrar Nuevo Usuario ---")
        nombre_usuario = input("Nombre de usuario (3-30 caracteres): ").strip()
        clave = getpass.getpass("Contraseña (8-128 caracteres, letras y números): ")
        confirmacion = getpass.getpass("Confirme la contraseña: ")

        print("Roles disponibles: 1.- Administrador, 2.- Gerente, 3.- Empleado, 4.- Operador")
        opcion_rol = leer_numero("Seleccione un rol (1-4): ")
        mapa_roles = {1: "Administrador", 2: "Gerente", 3: "Empleado", 4: "Operador"}
        rol = mapa_roles.get(opcion_rol, "")
        id_empleado = leer_id_opcional("ID de empleado asociado (opcional, Enter para omitir): ")

        return {
            "nombre_usuario": nombre_usuario,
            "clave": clave,
            "confirmacion": confirmacion,
            "rol": rol,
            "id_empleado": id_empleado,
        }

    @staticmethod
    def mostrar_lista_usuarios(usuarios: list[Usuario]) -> None:
        print("\n--- Lista de Usuarios Registrados ---")
        if not usuarios:
            print("No hay usuarios registrados.")
        else:
            for u in usuarios:
                print(u)
        print("-" * 68)

    @staticmethod
    def solicitar_id_usuario() -> int:
        return leer_numero("Ingrese el ID del usuario a eliminar: ")

    @staticmethod
    def confirmar_eliminacion(nombre_usuario: str) -> bool:
        return confirmar(f"¿Está seguro que desea eliminar al usuario '{nombre_usuario}'?")

    @staticmethod
    def mostrar_mensaje(mensaje: str) -> None:
        print(f"\n[AUTENTICACIÓN] {mensaje}")

    @staticmethod
    def mostrar_error(error: str) -> None:
        print(f"\n[ERROR DE CREDENCIALES] {error}")