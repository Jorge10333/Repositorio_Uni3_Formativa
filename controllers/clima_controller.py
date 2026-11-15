import logging  # Registra incidentes de API en logs/ecotech.log sin ensuciar la consola
from controllers.seguridad import exigir_sesion  # Exige usuario autenticado en cada acción
from exceptions import (  # Importa excepciones propias de red y validación
    ApiConexionError,
    ApiDatosInvalidosError,
    ApiHttpError,
    ApiTimeoutError,
    EcoTechError,
    ValidacionError,
)
from models.proyecto_dao import ProyectoDAO  # Verifica que el proyecto a vincular exista
from models.reporte_clima_dao import ReporteClimaDAO  # Guarda y consulta historial climático
from models.usuario import Usuario
from services.clima_service import ClimaService  # Servicio externo Open-Meteo
from views.clima_view import ClimaView

log = logging.getLogger(__name__)


class ClimaController:  # Orquesta el monitoreo climático para planificación de proyectos
    def __init__(self):
        self.view = ClimaView()

    def ejecutar(self, usuario_actual: Usuario) -> None:  # Menú principal del módulo de clima
        exigir_sesion(usuario_actual)
        while True:
            opcion = self.view.mostrar_menu()
            if opcion == 1:
                self.consultar_clima_ciudad(usuario_actual)
            elif opcion == 2:
                self.consultar_y_guardar_reporte(usuario_actual)
            elif opcion == 3:
                self.listar_historial(usuario_actual)
            elif opcion == 4:
                self.consultar_por_proyecto(usuario_actual)
            elif opcion == 5:
                self.diagnosticar_conexion(usuario_actual)
            elif opcion == 0:
                break
            else:
                self.view.mostrar_error("Opción no válida.")

    def _obtener_reporte_con_respaldo(self, ciudad: str):  # Consulta API y activa respaldo ante falla
        try:
            return ClimaService.consultar_clima(ciudad)  # Intenta obtener clima real desde Open-Meteo
        except ValidacionError as e:
            self.view.mostrar_error(str(e))  # Error de entrada del usuario (no activa contingencia)
            return None
        except (ApiTimeoutError, ApiConexionError, ApiHttpError, ApiDatosInvalidosError) as e:
            log.warning("Falla en Open-Meteo para '%s': %s", ciudad, e)
            self.view.mostrar_error(str(e))
            respaldo = ClimaService.obtener_respaldo(ciudad)  # Busca registro local de respaldo
            if respaldo is not None:
                self.view.mostrar_mensaje("[MODO CONTINGENCIA] Se cargó registro local de respaldo.")
                return respaldo
            return None

    def consultar_clima_ciudad(self, usuario_actual: Usuario) -> None:
        exigir_sesion(usuario_actual)
        ciudad = self.view.pedir_ciudad()
        reporte = self._obtener_reporte_con_respaldo(ciudad)
        if reporte:
            self.view.mostrar_reporte_actual(reporte)

    def consultar_y_guardar_reporte(self, usuario_actual: Usuario) -> None:
        exigir_sesion(usuario_actual)
        ciudad = self.view.pedir_ciudad()
        reporte = self._obtener_reporte_con_respaldo(ciudad)
        if not reporte:
            return

        self.view.mostrar_reporte_actual(reporte)
        if not self.view.confirmar_guardado():
            self.view.mostrar_mensaje("Guardado cancelado.")
            return

        id_proyecto = self.view.pedir_id_proyecto_opcional()
        if id_proyecto is not None and not ProyectoDAO.obtener_por_id(id_proyecto):
            self.view.mostrar_error(f"El proyecto #{id_proyecto} no existe en la base de datos.")
            return

        reporte.id_proyecto = id_proyecto
        reporte.id_usuario = usuario_actual.id_usuario

        id_generado = ReporteClimaDAO.insertar(reporte)
        if id_generado:
            self.view.mostrar_mensaje(f"Reporte #{id_generado} ({reporte.origen}) guardado con éxito.")
        else:
            self.view.mostrar_error("No fue posible guardar el reporte climático.")

    def listar_historial(self, usuario_actual: Usuario) -> None:
        exigir_sesion(usuario_actual)
        self.view.mostrar_historial(ReporteClimaDAO.listar_todos())

    def consultar_por_proyecto(self, usuario_actual: Usuario) -> None:
        exigir_sesion(usuario_actual)
        id_proyecto = self.view.pedir_id_proyecto_busqueda()
        self.view.mostrar_historial(ReporteClimaDAO.obtener_por_proyecto(id_proyecto))

    def diagnosticar_conexion(self, usuario_actual: Usuario) -> None:
        exigir_sesion(usuario_actual)
        try:
            _, detalle = ClimaService.probar_conectividad()
            self.view.mostrar_mensaje(f"[ONLINE] {detalle}")
        except EcoTechError as e:
            self.view.mostrar_error(f"[OFFLINE] {e}")