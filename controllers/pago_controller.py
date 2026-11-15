import logging  # Registra fallos de la API de divisas en el archivo de log
from controllers.seguridad import exigir_rol, exigir_sesion  # Control de permisos por rol
from exceptions import (
    ApiConexionError,
    ApiDatosInvalidosError,
    ApiHttpError,
    ApiTimeoutError,
    EcoTechError,
    ValidacionError,
)
from models.empleado_dao import EmpleadoDAO  # Valida existencia del empleado beneficiario
from models.pago_internacional import PagoInternacional  # Modelo con cálculo exacto Decimal
from models.pago_internacional_dao import PagoInternacionalDAO  # Persistencia en SQLite
from models.proyecto_dao import ProyectoDAO  # Valida existencia del proyecto asociado
from models.usuario import Usuario
from services.divisa_service import DivisaService  # Servicio externo Frankfurter API
from views.pago_view import PagoView

log = logging.getLogger(__name__)


class PagoController:  # Coordina tipos de cambio y pagos internacionales (Admin y Gerente)
    def __init__(self):
        self.view = PagoView()

    def ejecutar(self, usuario_actual: Usuario) -> None:  # Restringe acceso a roles autorizados
        exigir_rol(usuario_actual, "Administrador", "Gerente")
        while True:
            opcion = self.view.mostrar_menu()
            if opcion == 1:
                self.consultar_tasa(usuario_actual)
            elif opcion == 2:
                self.calcular_y_guardar_pago(usuario_actual)
            elif opcion == 3:
                self.listar_historial(usuario_actual)
            elif opcion == 4:
                self.diagnosticar_conexion(usuario_actual)
            elif opcion == 0:
                break
            else:
                self.view.mostrar_error("Opción no válida.")

    def consultar_tasa(self, usuario_actual: Usuario) -> None:
        exigir_rol(usuario_actual, "Administrador", "Gerente")
        origen, destino = self.view.pedir_par_monedas()
        try:
            tasa, fecha = DivisaService.obtener_tasa_cambio(origen, destino)
            self.view.mostrar_mensaje(f"Tasa oficial ({fecha}): 1 {origen} = {tasa:.4f} {destino}.")
        except ValidacionError as e:
            self.view.mostrar_error(str(e))
        except (ApiTimeoutError, ApiConexionError, ApiHttpError, ApiDatosInvalidosError) as e:
            log.warning("Falla API Divisas (%s->%s): %s", origen, destino, e)
            self.view.mostrar_error(str(e))
            respaldo = DivisaService.obtener_tasa_respaldo(origen, destino)
            if respaldo is not None:
                self.view.mostrar_mensaje(f"[MODO CONTINGENCIA] Tasa referencial: 1 {origen} = {respaldo:.4f} {destino}.")

    def calcular_y_guardar_pago(self, usuario_actual: Usuario) -> None:
        exigir_rol(usuario_actual, "Administrador", "Gerente")
        datos = self.view.formulario_pago_internacional(DivisaService.sugerir_moneda_por_pais)
        if not datos:
            return

        try:
            pais_valido = DivisaService.validar_pais(datos["pais_proyecto"])  # Exige país en catálogo
            origen_dato = "API"
            fecha_tasa = ""

            try:
                tasa, fecha_tasa = DivisaService.obtener_tasa_cambio(
                    datos["moneda_origen"], datos["moneda_destino"]
                )
            except (ApiTimeoutError, ApiConexionError, ApiHttpError, ApiDatosInvalidosError) as e:
                log.warning("Falla API Divisas al liquidar pago: %s", e)
                self.view.mostrar_error(str(e))
                tasa = DivisaService.obtener_tasa_respaldo(datos["moneda_origen"], datos["moneda_destino"])
                if tasa is None:
                    return
                origen_dato = "contingencia"

            pago = PagoInternacional(
                pais_proyecto=pais_valido,
                moneda_origen=datos["moneda_origen"],
                moneda_destino=datos["moneda_destino"],
                monto_base=datos["monto_base"],
                tasa_cambio=tasa,
                fecha_tasa=fecha_tasa,
                origen=origen_dato,
                id_empleado=datos["id_empleado"],
                id_proyecto=datos["id_proyecto"],
                id_usuario=usuario_actual.id_usuario,
            )

            self.view.mostrar_detalle_conversion(pago)  # Muestra el desglose calculado

            # Impide guardar pagos oficiales usando tasas de contingencia sin conexión
            if pago.origen == "contingencia":
                self.view.mostrar_error(
                    "Los pagos calculados en modo contingencia son solo referenciales y no se guardan en BD."
                )
                return

            if not self.view.confirmar_guardado():
                self.view.mostrar_mensaje("Cálculo descartado.")
                return

            if pago.id_empleado is not None and not EmpleadoDAO.obtener_por_id(pago.id_empleado):
                self.view.mostrar_error(f"El empleado #{pago.id_empleado} no existe en el sistema.")
                return
            if pago.id_proyecto is not None and not ProyectoDAO.obtener_por_id(pago.id_proyecto):
                self.view.mostrar_error(f"El proyecto #{pago.id_proyecto} no existe en el sistema.")
                return

            id_generado = PagoInternacionalDAO.insertar(pago)
            if id_generado:
                self.view.mostrar_mensaje(f"Pago internacional #{id_generado} registrado con éxito.")
            else:
                self.view.mostrar_error("No fue posible guardar el pago internacional.")

        except (ValidacionError, ValueError) as e:
            self.view.mostrar_error(str(e))

    def listar_historial(self, usuario_actual: Usuario) -> None:
        exigir_sesion(usuario_actual)
        self.view.mostrar_historial(PagoInternacionalDAO.listar_todos())

    def diagnosticar_conexion(self, usuario_actual: Usuario) -> None:
        exigir_sesion(usuario_actual)
        try:
            _, detalle = DivisaService.probar_conectividad()
            self.view.mostrar_mensaje(f"[ONLINE] {detalle}")
        except EcoTechError as e:
            self.view.mostrar_error(f"[OFFLINE] {e}")