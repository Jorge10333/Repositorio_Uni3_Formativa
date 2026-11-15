from controllers.auth_controller import AuthController
from controllers.clima_controller import ClimaController
from controllers.departamento_controller import DepartamentoController
from controllers.empleado_controller import EmpleadoController
from controllers.pago_controller import PagoController
from controllers.proyecto_controller import ProyectoController
from controllers.registro_tiempo_controller import RegistroTiempoController
from controllers.seguridad import exigir_sesion
from exceptions import AccesoDenegadoError
from models.usuario import Usuario
from views.main_view import MainView
from views.utils import leer_numero


class MainController:  # Controlador raíz que conecta todos los módulos de EcoTech Solutions
    def __init__(self):
        self.view = MainView()
        self.auth_controller = AuthController()
        self.empleado_controller = EmpleadoController()
        self.departamento_controller = DepartamentoController()
        self.proyecto_controller = ProyectoController()
        self.registro_tiempo_controller = RegistroTiempoController()
        self.clima_controller = ClimaController()
        self.pago_controller = PagoController()
        self.usuario_actual: Usuario | None = None

    def _submenu_personal(self) -> None:  # Conecta Empleados y Departamentos a la opción 1
        exigir_sesion(self.usuario_actual)
        while True:
            print("\n--- GESTIÓN DE EMPLEADOS Y DEPARTAMENTOS ---")
            print("1.- Gestión de Empleados")
            print("2.- Gestión de Departamentos")
            print("0.- Volver al menú principal")
            op = leer_numero("Seleccione una opción: ")
            if op == 1:
                self.empleado_controller.ejecutar()
            elif op == 2:
                self.departamento_controller.ejecutar()
            elif op == 0:
                break

    def _submenu_proyectos(self) -> None:  # Conecta Proyectos y Registro de Tiempo a la opción 2
        exigir_sesion(self.usuario_actual)
        while True:
            print("\n--- GESTIÓN DE PROYECTOS Y REGISTRO DE TIEMPO ---")
            print("1.- Gestión de Proyectos")
            print("2.- Registro de Horas Trabajadas")
            print("0.- Volver al menú principal")
            op = leer_numero("Seleccione una opción: ")
            if op == 1:
                self.proyecto_controller.ejecutar()
            elif op == 2:
                self.registro_tiempo_controller.ejecutar()
            elif op == 0:
                break

    def ejecutar(self) -> None:  # Exige login antes de permitir entrar al menú principal
        self.usuario_actual = self.auth_controller.iniciar_sesion()
        if not self.usuario_actual:
            self.view.mostrar_mensaje("El programa ha finalizado debido a credenciales inválidas.")
            return

        while True:
            opcion = self.view.mostrar_menu(self.usuario_actual)
            try:
                if opcion == 1:
                    self._submenu_personal()
                elif opcion == 2:
                    self._submenu_proyectos()
                elif opcion == 3:
                    self.clima_controller.ejecutar(self.usuario_actual)
                elif opcion == 4:
                    self.auth_controller.ejecutar(self.usuario_actual)
                elif opcion == 5:
                    self.pago_controller.ejecutar(self.usuario_actual)
                elif opcion == 9:
                    self.view.mostrar_mensaje(f"Cerrando sesión de '{self.usuario_actual.nombre_usuario}'...")
                    self.usuario_actual = None  # Limpia la sesión activa antes de pedir nuevo login
                    self.usuario_actual = self.auth_controller.iniciar_sesion()
                    if not self.usuario_actual:
                        self.view.mostrar_mensaje("El programa ha finalizado debido a credenciales inválidas.")
                        break
                elif opcion == 0:
                    self.view.mostrar_mensaje("Gracias por usar EcoTech Solutions. ¡Hasta luego!")
                    break
                else:
                    self.view.mostrar_mensaje("Opción no válida.")
            except AccesoDenegadoError as e:
                self.view.mostrar_mensaje(f"[ACCESO DENEGADO] {e}")