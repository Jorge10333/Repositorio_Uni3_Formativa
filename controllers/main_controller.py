from views.main_view import MainView  # Importa la vista principal
from controllers.auth_controller import AuthController  # Importa el controlador de autenticación
from controllers.clima_controller import ClimaController  # Importa el controlador de clima
from controllers.pago_controller import PagoController  # Importa el controlador de pagos internacionales
from models.usuario import Usuario  # Importa el modelo Usuario


class MainController:  # Controlador raíz de la aplicación
    def __init__(self):
        self.view = MainView()  # Instancia la vista principal
        self.auth_controller = AuthController()  # Instancia controlador de login
        self.clima_controller = ClimaController()  # Instancia controlador de clima
        self.pago_controller = PagoController()  # Instancia controlador de divisas y pagos internacionales
        self.usuario_actual: Usuario | None = None  # Almacena la sesión activa

    def ejecutar(self) -> None:  # Punto de entrada del flujo de control de la aplicación
        # 1. Exige superar el inicio de sesión con credenciales encriptadas antes de mostrar el menú
        self.usuario_actual = self.auth_controller.iniciar_sesion()
        if not self.usuario_actual:  # Si el login falló o agotó los intentos permitidos
            self.view.mostrar_mensaje("El programa ha finalizado debido a credenciales inválidas.")
            return  # Termina la ejecución de forma segura sin abrir el menú

        # 2. Bucle principal del sistema una vez autenticado correctamente
        while True:  # Mantiene el menú activo hasta que el usuario elija salir (0)
            opcion = self.view.mostrar_menu(self.usuario_actual)  # Muestra el menú con el usuario activo
            if opcion == 1:
                # Espacio para conectar tus controladores existentes de Empleados/Departamentos
                self.view.mostrar_mensaje("Módulo de Empleados y Departamentos.")
            elif opcion == 2:
                # Espacio para conectar tus controladores existentes de Proyectos/RegistroTiempo
                self.view.mostrar_mensaje("Módulo de Proyectos y Registro de Tiempo.")
            elif opcion == 3:
                self.clima_controller.ejecutar(self.usuario_actual)  # Abre el módulo de clima pasando el usuario activo
            elif opcion == 4:
                self.auth_controller.ejecutar(self.usuario_actual)  # Abre la gestión de usuarios
            elif opcion == 5:
                self.pago_controller.ejecutar(self.usuario_actual)  # Abre el módulo de pagos internacionales
            elif opcion == 9:
                # Cierra la sesión actual y vuelve a pedir usuario y contraseña
                self.view.mostrar_mensaje(f"Cerrando sesión de '{self.usuario_actual.nombre_usuario}'...")
                self.usuario_actual = self.auth_controller.iniciar_sesion()  # Solicita nuevo inicio de sesión
                if not self.usuario_actual:  # Si el nuevo usuario falla el login, cierra el sistema
                    self.view.mostrar_mensaje("El programa ha finalizado debido a credenciales inválidas.")
                    break
            elif opcion == 0:
                self.view.mostrar_mensaje("Gracias por usar EcoTech Solutions. ¡Hasta luego!")
                break  # Rompe el ciclo y finaliza la aplicación
            else:
                self.view.mostrar_mensaje("Opción no válida. Por favor, intente nuevamente.")