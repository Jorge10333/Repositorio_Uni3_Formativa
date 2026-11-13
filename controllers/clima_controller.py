from views.clima_view import ClimaView  # Importa la vista del módulo climático
from services.clima_service import ClimaService  # Importa el servicio que consume la API Open-Meteo
from models.reporte_clima_dao import ReporteClimaDAO  # Importa el DAO para guardar reportes en SQLite
from models.usuario import Usuario  # Importa el modelo Usuario para registrar quién hizo la consulta


class ClimaController:  # Define el controlador del módulo de clima
    """
    Controlador que coordina la vista de clima, el servicio Open-Meteo y la persistencia local.
    """

    def __init__(self):  # Constructor del controlador
        self.view = ClimaView()  # Instancia la vista de clima
        self.service = ClimaService()  # Instancia el servicio externo
        self.reporte_dao = ReporteClimaDAO()  # Instancia el DAO de reportes climáticos

    def ejecutar(self, usuario_actual: Usuario | None = None) -> None:  # Bucle principal del módulo clima
        while True:  # Mantiene el submenú activo hasta seleccionar 0
            opcion = self.view.mostrar_menu()  # Muestra opciones y lee selección
            if opcion == 1:
                self.consultar_clima_ciudad()  # Solo consulta en tiempo real sin guardar
            elif opcion == 2:
                self.consultar_y_guardar_reporte(usuario_actual)  # Consulta en API y guarda en SQLite
            elif opcion == 3:
                self.listar_historial()  # Muestra todos los reportes guardados
            elif opcion == 4:
                self.consultar_por_proyecto()  # Filtra reportes guardados por ID de proyecto
            elif opcion == 5:
                self.diagnosticar_conexion()  # Verifica conectividad con Open-Meteo
            elif opcion == 0:
                break  # Regresa al menú principal
            else:
                self.view.mostrar_error("Opción no válida. Intente nuevamente.")

    def consultar_clima_ciudad(self) -> None:  # Consulta el clima actual sin persistirlo
        ciudad = self.view.pedir_ciudad()  # Solicita el nombre de la ciudad
        if not ciudad:  # Valida que no esté vacío
            self.view.mostrar_error("Debe ingresar el nombre de una ciudad.")
            return
        try:  # Protege contra errores de validación o red
            reporte, estado = self.service.consultar_clima(ciudad)  # Llama al servicio externo
            self.view.mostrar_mensaje(estado)  # Muestra el estado de la operación (ONLINE u OFFLINE)
            if reporte:  # Si se obtuvo un reporte válido
                self.view.mostrar_reporte_actual(reporte)  # Muestra temperatura y viento en pantalla
        except ValueError as e:  # Captura errores de sanitización de ciudad
            self.view.mostrar_error(str(e))
        except Exception as e:  # Captura cualquier otro error inesperado
            self.view.mostrar_error(f"Error inesperado al consultar clima: {e}")

    def consultar_y_guardar_reporte(self, usuario_actual: Usuario | None = None) -> None:  # Consulta y guarda en BD
        ciudad = self.view.pedir_ciudad()  # Pide la ciudad
        if not ciudad:
            self.view.mostrar_error("Debe ingresar el nombre de una ciudad.")
            return
        try:
            reporte, estado = self.service.consultar_clima(ciudad)  # Consulta la API Open-Meteo
            self.view.mostrar_mensaje(estado)  # Informa resultado de la consulta
            if not reporte:  # Si no se encontraron datos, cancela el guardado
                return

            self.view.mostrar_reporte_actual(reporte)  # Muestra los datos obtenidos antes de guardar
            if not self.view.confirmar_guardado():  # Pregunta al usuario si desea persistir el reporte
                self.view.mostrar_mensaje("Guardado cancelado.")
                return

            # Asocia opcionalmente el reporte a un proyecto y registra el ID del usuario conectado
            reporte.id_proyecto = self.view.pedir_id_proyecto_opcional()
            reporte.id_usuario = usuario_actual.id_usuario if usuario_actual else None

            id_generado = self.reporte_dao.insertar(reporte)  # Inserta el reporte en SQLite
            if id_generado:  # Si la inserción fue exitosa
                reporte.id_reporte = id_generado  # Actualiza el ID en el objeto
                self.view.mostrar_mensaje(
                    f"Reporte climático #{id_generado} guardado con éxito en ecotech_solutions.db."
                )
            else:
                self.view.mostrar_error(
                    "No se pudo guardar el reporte (verifique que el ID de proyecto exista si ingresó uno)."
                )
        except ValueError as e:
            self.view.mostrar_error(str(e))
        except Exception as e:
            self.view.mostrar_error(f"Error al registrar reporte: {e}")

    def listar_historial(self) -> None:  # Lista todos los reportes guardados en SQLite
        reportes = self.reporte_dao.listar_todos()  # Obtiene los registros desde el DAO
        self.view.mostrar_historial(reportes)  # Los muestra en consola

    def consultar_por_proyecto(self) -> None:  # Busca reportes asociados a un proyecto
        id_proyecto = self.view.pedir_id_proyecto_busqueda()  # Pide el ID del proyecto
        reportes = self.reporte_dao.obtener_por_proyecto(id_proyecto)  # Consulta en SQLite
        self.view.mostrar_historial(reportes)  # Muestra los resultados

    def diagnosticar_conexion(self) -> None:  # Ejecuta prueba de conectividad con Open-Meteo
        self.view.mostrar_mensaje("Verificando conectividad con Open-Meteo...")
        exito, detalle = self.service.probar_conectividad()  # Prueba conexión HTTP
        if exito:
            self.view.mostrar_mensaje(f"[ONLINE] {detalle}")
        else:
            self.view.mostrar_error(f"[OFFLINE] {detalle}")