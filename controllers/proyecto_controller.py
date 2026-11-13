from models.proyecto import Proyecto
from models.proyecto_dao import ProyectoDAO
from models.empleado_dao import EmpleadoDAO
from models.empleado_proyecto import EmpleadoProyecto
from models.empleado_proyecto_dao import EmpleadoProyectoDAO
from views.proyecto_view import ProyectoView

class ProyectoController:
    def __init__(self):
        self.view = ProyectoView()

    def ejecutar(self) -> None:
        while True:
            opcion = self.view.mostrar_menu()
            if opcion == 1:
                self.crear_proyecto()
            elif opcion == 2:
                self.editar_proyecto()
            elif opcion == 3:
                self.asignar_empleado()
            elif opcion == 4:
                self.desasignar_empleado()
            elif opcion == 5:
                self.imprimir_proyecto()
            elif opcion == 6:
                self.imprimir_proyectos()
            elif opcion == 7:
                self.eliminar_proyecto()
            elif opcion == 0:
                self.view.mostrar_mensaje("Saliendo de la gestión de proyectos.")
                break
            else:
                self.view.mostrar_mensaje("Opción no válida.")

    def crear_proyecto(self) -> None:
        datos = self.view.formulario_nuevo_proyecto()
        try:
            proyecto = Proyecto(datos['nombre'], datos['descripcion'], datos['fecha_inicio'])
            exito = ProyectoDAO.crear(proyecto)
            if exito:
                self.view.mostrar_mensaje(f"Proyecto creado exitosamente con ID {proyecto.id_proyecto}.")
            else:
                self.view.mostrar_mensaje("Error al guardar en la base de datos.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos ingresados: {e}")

    def editar_proyecto(self) -> None:
        id_proy = self.view.solicitar_id()
        proyecto = ProyectoDAO.obtener_por_id(id_proy)
        if not proyecto:
            self.view.mostrar_mensaje("Proyecto no encontrado.")
            return

        datos = self.view.formulario_editar_proyecto(proyecto)
        try:
            proyecto.nombre = datos['nombre']
            proyecto.descripcion = datos['descripcion']
            proyecto.fecha_inicio = datos['fecha_inicio']
            exito = ProyectoDAO.actualizar(proyecto)
            if exito:
                self.view.mostrar_mensaje("Proyecto actualizado exitosamente.")
            else:
                self.view.mostrar_mensaje("Error al actualizar.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en la edición: {e}")

    def asignar_empleado(self) -> None:
        id_emp = self.view.solicitar_id_empleado()
        if not EmpleadoDAO.obtener_por_id(id_emp):
            self.view.mostrar_mensaje(f"❌ El empleado con ID {id_emp} no existe.")
            return

        id_proy = self.view.solicitar_id()
        if not ProyectoDAO.obtener_por_id(id_proy):
            self.view.mostrar_mensaje(f"❌ El proyecto con ID {id_proy} no existe.")
            return

        asignacion = EmpleadoProyecto(id_empleado=id_emp, id_proyecto=id_proy)
        exito = EmpleadoProyectoDAO.asignar(asignacion)
        if exito:
            self.view.mostrar_mensaje("Empleado asignado correctamente al proyecto.")
        else:
            self.view.mostrar_mensaje("Error al asignar (posiblemente ya está asignado).")

    def desasignar_empleado(self) -> None:
        id_emp = self.view.solicitar_id_empleado()
        id_proy = self.view.solicitar_id()
        exito = EmpleadoProyectoDAO.desasignar(id_emp, id_proy)
        if exito:
            self.view.mostrar_mensaje("Empleado desasignado correctamente del proyecto.")
        else:
            self.view.mostrar_mensaje("Error al desasignar empleado.")

    def eliminar_proyecto(self) -> None:
        id_proy = self.view.solicitar_id()
        proyecto = ProyectoDAO.obtener_por_id(id_proy)
        if not proyecto:
            self.view.mostrar_mensaje("Proyecto no encontrado.")
            return

        if self.view.confirmar_eliminacion(proyecto.nombre):
            exito = ProyectoDAO.eliminar(id_proy)
            if exito:
                self.view.mostrar_mensaje("Proyecto eliminado exitosamente.")
            else:
                self.view.mostrar_mensaje("Error al eliminar de la base de datos.")

    def imprimir_proyecto(self) -> None:
        id_proy = self.view.solicitar_id()
        proyecto = ProyectoDAO.obtener_por_id(id_proy)
        if proyecto:
            self.view.mostrar_proyecto(proyecto)
        else:
            self.view.mostrar_mensaje("Proyecto no encontrado.")

    def imprimir_proyectos(self) -> None:
        proyectos = ProyectoDAO.obtener_todos()
        self.view.mostrar_lista_proyectos(proyectos)