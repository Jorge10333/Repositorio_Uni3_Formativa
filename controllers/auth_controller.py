import time  # Iguala tiempos de respuesta cuando el usuario no existe (evita enumeración de cuentas)
from config.settings import Settings  # Lee el máximo de intentos y minutos de bloqueo
from controllers.seguridad import exigir_rol  # Restringe la gestión de cuentas solo a Administradores
from models.empleado_dao import EmpleadoDAO  # Verifica que el empleado asociado exista en BD
from models.usuario import Usuario  # Modelo con validación de política y hash scrypt
from models.usuario_dao import UsuarioDAO  # Persistencia de usuarios y bloqueo en SQLite
from views.auth_view import AuthView  # Interfaz de consola para login y usuarios


class AuthController:  # Coordina el inicio de sesión y la administración de cuentas
    def __init__(self):
        self.view = AuthView()

    def iniciar_sesion(self) -> Usuario | None:  # Controla intentos de acceso y bloqueo en BD
        UsuarioDAO.inicializar_admin()  # Pide crear el admin inicial si la base de datos está vacía
        max_intentos = Settings.MAX_LOGIN_ATTEMPTS  # Límite configurable desde .env

        for intento in range(1, max_intentos + 1):
            self.view.mostrar_banner_login(intento, max_intentos)  # Muestra el encabezado de login
            credenciales = self.view.solicitar_credenciales()  # Pide usuario y clave oculta con getpass
            nombre_usuario = credenciales["nombre_usuario"]
            clave = credenciales["clave"]

            # Valida formato básico antes de consultar la base de datos
            es_valido, mensaje = Usuario.validar_credenciales_ingreso(nombre_usuario, clave)
            if not es_valido:
                self.view.mostrar_error(mensaje)
                continue

            usuario_bd = UsuarioDAO.obtener_por_username(nombre_usuario)  # Busca la cuenta en SQLite
            if usuario_bd is not None:
                bloqueado, msg_bloqueo = usuario_bd.esta_bloqueado()  # Revisa si sigue bloqueada en BD
                if bloqueado:
                    self.view.mostrar_error(msg_bloqueo)
                    continue

                if usuario_bd.verificar_credencial(clave):  # Compara el hash scrypt en tiempo constante
                    UsuarioDAO.reiniciar_intentos(usuario_bd)  # Limpia contador de fallos en BD
                    self.view.mostrar_bienvenida(usuario_bd)
                    return usuario_bd  # Devuelve el usuario autenticado

                # Registra el intento fallido en SQLite y activa bloqueo si llegó al límite
                _, quedo_bloqueado = UsuarioDAO.registrar_intento_fallido(usuario_bd)
                if quedo_bloqueado:
                    self.view.mostrar_error(
                        f"Cuenta bloqueada por {Settings.LOCKOUT_MINUTES} minutos tras {max_intentos} fallos."
                    )
                    return None
            else:
                time.sleep(0.25)  # Simula tiempo de cómputo para no revelar si el usuario existe

            self.view.mostrar_error("Credenciales incorrectas.")  # Mensaje genérico sin pistas al atacante

        self.view.mostrar_error("Se agotaron los intentos permitidos. Acceso denegado.")
        return None

    def ejecutar(self, usuario_actual: Usuario) -> None:  # Submenú exclusivo para Administradores
        exigir_rol(usuario_actual, "Administrador")  # Bloquea entrada directa sin rol Administrador
        while True:
            opcion = self.view.mostrar_menu_usuarios()
            if opcion == 1:
                self.registrar_usuario(usuario_actual)
            elif opcion == 2:
                self.listar_usuarios(usuario_actual)
            elif opcion == 3:
                self.eliminar_usuario(usuario_actual)
            elif opcion == 0:
                break
            else:
                self.view.mostrar_error("Opción no válida.")

    def registrar_usuario(self, usuario_actual: Usuario) -> None:
        exigir_rol(usuario_actual, "Administrador")
        datos = self.view.formulario_nuevo_usuario()

        if datos["clave"] != datos["confirmacion"]:  # Comprueba que ambas claves coincidan
            self.view.mostrar_error("Las contraseñas ingresadas no coinciden.")
            return

        if UsuarioDAO.obtener_por_username(datos["nombre_usuario"]):  # Evita nombres duplicados
            self.view.mostrar_error("El nombre de usuario ya está registrado.")
            return

        if datos["id_empleado"] is not None and not EmpleadoDAO.obtener_por_id(datos["id_empleado"]):
            self.view.mostrar_error(f"El empleado #{datos['id_empleado']} no existe.")
            return

        try:
            clave_hash = Usuario.encriptar_credencial(datos["clave"])  # Genera hash scrypt con sal
            nuevo = Usuario(
                nombre_usuario=datos["nombre_usuario"],
                contrasena_hash=clave_hash,
                rol=datos["rol"],
                id_empleado=datos["id_empleado"],
            )
            if UsuarioDAO.crear(nuevo):
                self.view.mostrar_mensaje(f"Usuario '{nuevo.nombre_usuario}' creado con éxito.")
            else:
                self.view.mostrar_error("No fue posible guardar el usuario.")
        except ValueError as e:
            self.view.mostrar_error(str(e))

    def listar_usuarios(self, usuario_actual: Usuario) -> None:
        exigir_rol(usuario_actual, "Administrador")
        self.view.mostrar_lista_usuarios(UsuarioDAO.obtener_todos())

    def eliminar_usuario(self, usuario_actual: Usuario) -> None:
        exigir_rol(usuario_actual, "Administrador")
        id_usuario = self.view.solicitar_id_usuario()
        usuario = UsuarioDAO.obtener_por_id(id_usuario)
        if not usuario:
            self.view.mostrar_error("Usuario no encontrado.")
            return
        if usuario.id_usuario == usuario_actual.id_usuario:  # Impide que el admin se borre a sí mismo
            self.view.mostrar_error("No puede eliminar su propio usuario mientras está conectado.")
            return
        if self.view.confirmar_eliminacion(usuario.nombre_usuario):
            if UsuarioDAO.eliminar(id_usuario):
                self.view.mostrar_mensaje(f"Usuario '{usuario.nombre_usuario}' eliminado.")
            else:
                self.view.mostrar_error("No fue posible eliminar el usuario.")