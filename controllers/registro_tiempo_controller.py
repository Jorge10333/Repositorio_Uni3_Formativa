# --- Controlador de Registro de Tiempo ---
from models.registro_tiempo import RegistroTiempo
from models.registro_tiempo_dao import RegistroTiempoDAO
from views.registro_tiempo_view import RegistroTiempoView

class RegistroTiempoController:
    def __init__(self):
        self.view = RegistroTiempoView()

    def ejecutar(self) -> None:
        while True:
            opcion = self.view.mostrar_menu()
            if opcion == 1:
                self.registrar_horas()
            elif opcion == 2:
                self.ver_horas_empleado()
            elif opcion == 3:
                self.eliminar_registro()
            elif opcion == 0:
                self.view.mostrar_mensaje("Saliendo del registro de tiempo.")
                break
            else:
                self.view.mostrar_mensaje("Opción no válida.")

    def registrar_horas(self) -> None:
        # Registra las horas trabajadas en BD
        datos = self.view.formulario_nuevo_registro()
        try:
            registro = RegistroTiempo(**datos)
            exito = RegistroTiempoDAO.crear(registro)
            if exito:
                self.view.mostrar_mensaje(f"Registro guardado con éxito (ID: {registro.id_registro}).")
            else:
                self.view.mostrar_mensaje("Error al guardar en la base de datos.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos ingresados: {e}")

    def ver_horas_empleado(self) -> None:
        # Obtiene lista de horas de un empleado
        id_emp = self.view.solicitar_id_empleado()
        registros = RegistroTiempoDAO.obtener_por_empleado(id_emp)
        self.view.mostrar_lista_registros(registros)

    def eliminar_registro(self) -> None:
        id_reg = self.view.solicitar_id_registro()
        exito = RegistroTiempoDAO.eliminar(id_reg)
        if exito:
            self.view.mostrar_mensaje("Registro de tiempo eliminado correctamente.")
        else:
            self.view.mostrar_mensaje("Error al eliminar o registro no encontrado.")