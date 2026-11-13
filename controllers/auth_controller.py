from config.settings import Settings  # Importa el límite máximo de intentos desde Settings
from models.usuario import Usuario  # Importa el modelo Usuario para validaciones y hash
from models.usuario_dao import UsuarioDAO  # Importa el DAO para consultar/guardar usuarios en SQLite
from views.auth_view import AuthView  # Importa la vista de autenticación


class AuthController:  # Define el controlador que orquesta el inicio de sesión y gestión de cuentas
    """
    Controlador de Autenticación y Gestión de Usuarios para EcoTech Solutions.
    """

    def __init__(self):  # Constructor del controlador
        self.view = AuthView()  # Instancia la vista asociada

    def iniciar_sesion(self) -> Usuario | None:  # Controla el flujo completo de login antes de entrar al menú
        UsuarioDAO.inicializar_admin_por_defecto()  # Asegura que exista el usuario admin inicial en BD
        max_intentos = Settings.MAX_LOGIN_ATTEMPTS  # Obtiene el límite de intentos permitidos (ej. 3)

        for intento in range(1, max_intentos + 1):  # Itera desde el intento 1 hasta max_intentos
            self.view.mostrar_banner_login(intento, max_intentos)  # Muestra el encabezado del login
            credenciales = self.view.solicitar_credenciales()  # Pide usuario y contraseña por consola
            nombre_usuario = credenciales["nombre_usuario"]  # Extrae el usuario ingresado
            clave = credenciales["clave"]  # Extrae la contraseña ingresada

            # 1. Validación preventiva: rechaza entradas vacías o con caracteres inválidos antes de ir a BD
            es_valido, mensaje_validacion = Usuario.validar_credenciales_ingreso(nombre_usuario, clave)
            if not es_valido:  # Si las entradas vienen vacías o malformadas
                self.view.mostrar_error(f"Validación fallida: {mensaje_validacion}")  # Informa el error
                continue  # Pasa al siguiente intento sin consultar la base de datos

            # 2. Busca el usuario en SQLite y verifica su hash SHA-256 en tiempo constante
            usuario_bd = UsuarioDAO.obtener_por_username(nombre_usuario)  # Consulta el usuario en la tabla usuario
            if usuario_bd is not None and usuario_bd.verificar_credencial(clave):  # Verifica existencia y clave
                self.view.mostrar_bienvenida(usuario_bd)  # Muestra saludo de acceso concedido
                return usuario_bd  # Retorna el objeto Usuario autenticado al MainController

            # Muestra mensaje genérico para no revelar si falló el usuario o la contraseña
            self.view.mostrar_error(
                "Credenciales incorrectas: el usuario no existe o la contraseña no coincide."
            )

        # Si se agotan todos los intentos permitidos, bloquea el acceso
        self.view.mostrar_error(
            f"Ha superado el número máximo de intentos permitidos ({max_intentos}). "
            "Acceso bloqueado por seguridad."
        )
        return None  # Retorna None indicando que el acceso fue denegado

    def ejecutar(self, usuario_actual: Usuario | None = None) -> None:  # Bucle del submenú de gestión de usuarios
        while True:  # Mantiene activo el submenú hasta que el usuario elija 0
            opcion = self.view.mostrar_menu_usuarios()  # Muestra opciones y lee selección
            if opcion == 1:
                self.registrar_usuario()  # Llama al flujo de creación de usuario
            elif opcion == 2:
                self.listar_usuarios()  # Llama al flujo de listado
            elif opcion == 3:
                self.eliminar_usuario(usuario_actual)  # Llama al flujo de eliminación protegiendo la sesión activa
            elif opcion == 0:
                self.view.mostrar_mensaje("Saliendo de la gestión de usuarios.")
                break  # Sale del submenú y regresa al menú principal
            else:
                self.view.mostrar_error("Opción no válida.")

    def registrar_usuario(self) -> None:  # Orquesta el registro de una nueva cuenta con clave encriptada
        datos = self.view.formulario_nuevo_usuario()  # Solicita los datos mediante la vista

        # Valida que el usuario y contraseña cumplan el formato mínimo
        es_valido, msg = Usuario.validar_credenciales_ingreso(datos["nombre_usuario"], datos["clave"])
        if not es_valido:
            self.view.mostrar_error(msg)
            return  # Cancela el registro si hay datos vacíos o inválidos

        if datos["clave"] != datos["confirmacion"]:  # Verifica que ambas contraseñas coincidan
            self.view.mostrar_error("Las contraseñas ingresadas no coinciden.")
            return  # Cancela el registro

        if UsuarioDAO.obtener_por_username(datos["nombre_usuario"]):  # Verifica si el username ya está ocupado
            self.view.mostrar_error(f"Ya existe un usuario registrado con el login '{datos['nombre_usuario']}'.")
            return  # Cancela el registro

        try:  # Protege la instanciación y el guardado en base de datos
            password_encriptada = Usuario.encriptar_credencial(datos["clave"])  # Genera el hash SHA-256
            nuevo_usuario = Usuario(  # Crea el objeto Usuario con la clave ya encriptada
                nombre_usuario=datos["nombre_usuario"],
                contrasena_hash=password_encriptada,
                rol=datos["rol"],
                id_empleado=datos["id_empleado"]
            )
            if UsuarioDAO.crear(nuevo_usuario):  # Guarda el usuario en SQLite mediante el DAO
                self.view.mostrar_mensaje(
                    f"Usuario '{nuevo_usuario.nombre_usuario}' registrado exitosamente con credencial encriptada."
                )
            else:
                self.view.mostrar_error("No fue posible guardar el usuario en la base de datos.")
        except (ValueError, TypeError) as e:  # Captura errores de validación de los setters del modelo
            self.view.mostrar_error(f"Datos inválidos: {e}")

    def listar_usuarios(self) -> None:  # Obtiene y muestra todos los usuarios registrados
        usuarios = UsuarioDAO.obtener_todos()  # Pide la lista al DAO
        self.view.mostrar_lista_usuarios(usuarios)  # Envía la lista a la vista para imprimirla

    def eliminar_usuario(self, usuario_actual: Usuario | None = None) -> None:  # Elimina una cuenta de usuario
        id_usuario = self.view.solicitar_id_usuario()  # Pide el ID a eliminar
        usuario = UsuarioDAO.obtener_por_id(id_usuario)  # Busca si existe ese ID en SQLite
        if not usuario:  # Si no existe
            self.view.mostrar_error("Usuario no encontrado.")
            return

        # Impide que el usuario conectado borre su propia cuenta mientras está en sesión
        if usuario_actual and usuario.id_usuario == usuario_actual.id_usuario:
            self.view.mostrar_error("No puede eliminar su propio usuario con la sesión activa.")
            return

        if self.view.confirmar_eliminacion(usuario.nombre_usuario):  # Pide confirmación al operador
            if UsuarioDAO.eliminar(id_usuario):  # Ejecuta DELETE en SQLite
                self.view.mostrar_mensaje(f"Usuario '{usuario.nombre_usuario}' eliminado exitosamente.")
            else:
                self.view.mostrar_error("Error al eliminar el usuario en la base de datos.")
        else:
            self.view.mostrar_mensaje("Operación cancelada.")