from views.pago_view import PagoView  # Importa la vista de pagos internacionales
from services.divisa_service import DivisaService  # Importa el servicio que consulta Frankfurter API
from models.pago_internacional import PagoInternacional  # Importa el modelo de dominio
from models.pago_internacional_dao import PagoInternacionalDAO  # Importa el DAO de persistencia SQLite
from models.usuario import Usuario  # Importa el modelo Usuario para auditar quién autorizó el pago


class PagoController:  # Define el controlador que orquesta el cálculo de pagos con tipo de cambio
    """
    Controlador para gestionar pagos internacionales ajustados por indicadores económicos.
    """

    def __init__(self):  # Constructor del controlador
        self.view = PagoView()  # Instancia la vista
        self.service = DivisaService()  # Instancia el servicio externo
        self.pago_dao = PagoInternacionalDAO()  # Instancia el DAO

    def ejecutar(self, usuario_actual: Usuario | None = None) -> None:  # Bucle principal del submenú
        while True:  # Mantiene activo el submenú hasta seleccionar 0
            opcion = self.view.mostrar_menu()  # Muestra opciones y captura selección
            if opcion == 1:
                self.consultar_tasa()  # Consulta puntual de tasa de cambio
            elif opcion == 2:
                self.calcular_y_guardar_pago(usuario_actual)  # Calcula conversión y guarda en BD
            elif opcion == 3:
                self.listar_historial()  # Lista pagos guardados
            elif opcion == 4:
                self.diagnosticar_conexion()  # Verifica conectividad con Frankfurter API
            elif opcion == 0:
                break  # Vuelve al menú principal
            else:
                self.view.mostrar_error("Opción no válida. Intente nuevamente.")

    def consultar_tasa(self) -> None:  # Consulta una tasa en tiempo real sin guardar en BD
        origen, destino = self.view.pedir_par_monedas()  # Pide ambas monedas
        try:  # Protege contra códigos inválidos o errores de red
            tasa, fecha, mensaje = self.service.obtener_tasa_cambio(origen, destino)  # Llama al servicio
            if tasa is not None:  # Si se obtuvo la tasa
                self.view.mostrar_mensaje(mensaje)
            else:
                self.view.mostrar_error(mensaje)
        except ValueError as e:  # Captura errores de formato ISO
            self.view.mostrar_error(str(e))

    def calcular_y_guardar_pago(self, usuario_actual: Usuario | None = None) -> None:  # Calcula y guarda pago
        datos = self.view.formulario_pago_internacional(self.service.sugerir_moneda_por_pais)
        if not datos:  # Si el formulario fue cancelado o tuvo datos inválidos
            return

        try:  # Protege la consulta a la API y la creación del modelo
            tasa, fecha_tasa, mensaje = self.service.obtener_tasa_cambio(
                datos["moneda_origen"],
                datos["moneda_destino"]
            )  # Consulta la tasa actualizada en Frankfurter API
            self.view.mostrar_mensaje(mensaje)  # Informa el origen de la tasa (online o contingencia)

            if tasa is None:  # Si no se pudo obtener tasa ni de respaldo
                return

            # Instancia el objeto de dominio PagoInternacional (calcula automáticamente el total convertido)
            pago = PagoInternacional(
                pais_proyecto=datos["pais_proyecto"],
                moneda_origen=datos["moneda_origen"],
                moneda_destino=datos["moneda_destino"],
                monto_base=datos["monto_base"],
                tasa_cambio=tasa,
                fecha_tasa=fecha_tasa,
                id_empleado=datos["id_empleado"],
                id_proyecto=datos["id_proyecto"],
                id_usuario=usuario_actual.id_usuario if usuario_actual else None
            )

            self.view.mostrar_detalle_conversion(pago)  # Muestra el resumen antes de guardar

            if not self.view.confirmar_guardado():  # Pide confirmación al operador
                self.view.mostrar_mensaje("Cálculo descartado; no se guardó en la base de datos.")
                return

            id_generado = self.pago_dao.insertar(pago)  # Guarda en SQLite mediante el DAO
            if id_generado:  # Si la inserción fue exitosa
                pago.id_pago = id_generado
                self.view.mostrar_mensaje(f"Pago internacional #{id_generado} registrado exitosamente en SQLite.")
            else:
                self.view.mostrar_error(
                    "No se pudo guardar el pago (verifique que el ID de empleado o proyecto exista)."
                )
        except ValueError as e:  # Captura errores de validación del modelo
            self.view.mostrar_error(str(e))
        except Exception as e:  # Captura cualquier error inesperado
            self.view.mostrar_error(f"Error inesperado al calcular pago: {e}")

    def listar_historial(self) -> None:  # Muestra todos los pagos guardados
        pagos = self.pago_dao.listar_todos()  # Consulta SQLite
        self.view.mostrar_historial(pagos)  # Imprime en consola

    def diagnosticar_conexion(self) -> None:  # Verifica el estado de Frankfurter API
        self.view.mostrar_mensaje("Verificando conectividad con Frankfurter API...")
        exito, detalle = self.service.probar_conectividad()
        if exito:
            self.view.mostrar_mensaje(f"[ONLINE] {detalle}")
        else:
            self.view.mostrar_error(f"[OFFLINE] {detalle}")