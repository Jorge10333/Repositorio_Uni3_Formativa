from models.empleado import Empleado
from models.empleado_dao import EmpleadoDAO
from models.departamento_dao import DepartamentoDAO
from views.empleado_view import EmpleadoView

class EmpleadoController:
    """
    Controlador encargado de coordinar la lógica de negocio de Empleados.
    """
    def __init__(self):
        self.view = EmpleadoView()

    def ejecutar(self) -> None:
        # Bucle del submenú de empleados
        while True:
            opcion = self.view.mostrar_menu()
            if opcion == 1:
                self.agregar_empleado()
            elif opcion == 2:
                self.editar_empleado()
            elif opcion == 3:
                self.eliminar_empleado()
            elif opcion == 4:
                self.imprimir_empleado()
            elif opcion == 5:
                self.imprimir_empleados()
            elif opcion == 0:
                self.view.mostrar_mensaje("Saliendo de la gestión de empleados.")
                break
            else:
                self.view.mostrar_mensaje("Opción no válida.")

    def agregar_empleado(self) -> None:
        # Pide departamentos para la selección y registra el objeto empleado
        departamentos = DepartamentoDAO.obtener_todos()
        datos = self.view.formulario_nuevo_empleado(departamentos)
        try:
            depto_seleccionado = None
            if datos.get('id_departamento'):
                depto_seleccionado = DepartamentoDAO.obtener_por_id(datos['id_departamento'])

            nuevo_empleado = Empleado(
                nombre=datos['nombre'],
                direccion=datos['direccion'],
                telefono=datos['telefono'],
                email=datos['email'],
                fecha_inicio=datos['fecha_inicio'],
                salario=datos['salario'],
                departamento=depto_seleccionado
            )
            exito = EmpleadoDAO.crear(nuevo_empleado)
            if exito:
                self.view.mostrar_mensaje(f"Empleado registrado exitosamente con ID {nuevo_empleado.id_unico}.")
            else:
                self.view.mostrar_mensaje("Error al guardar en la base de datos.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos ingresados: {e}")

    def editar_empleado(self) -> None:
        # Edita campos específicos del empleado en la base de datos
        id_emp = self.view.solicitar_id()
        empleado = EmpleadoDAO.obtener_por_id(id_emp)
        if not empleado:
            self.view.mostrar_mensaje("Empleado no encontrado.")
            return

        departamentos = DepartamentoDAO.obtener_todos()
        datos = self.view.formulario_editar_empleado(empleado, departamentos)
        try:
            empleado.nombre = datos['nombre']
            empleado.direccion = datos['direccion']
            empleado.telefono = datos['telefono']
            empleado.email = datos['email']
            empleado.fecha_inicio = datos['fecha_inicio']
            empleado.salario = datos['salario']

            depto_seleccionado = None
            if datos.get('id_departamento'):
                depto_seleccionado = DepartamentoDAO.obtener_por_id(datos['id_departamento'])
            empleado.departamento = depto_seleccionado

            exito = EmpleadoDAO.actualizar(empleado)
            if exito:
                self.view.mostrar_mensaje("Empleado actualizado exitosamente.")
            else:
                self.view.mostrar_mensaje("Error al actualizar en la base de datos.")
        except (ValueError, TypeError) as e:
            self.view.mostrar_mensaje(f"Error en los datos modificados: {e}")

    def eliminar_empleado(self) -> None:
        # Pide confirmación y remueve al empleado
        id_emp = self.view.solicitar_id()
        empleado = EmpleadoDAO.obtener_por_id(id_emp)
        if not empleado:
            self.view.mostrar_mensaje("Empleado no encontrado.")
            return

        if self.view.confirmar_eliminacion(empleado.nombre):
            exito = EmpleadoDAO.eliminar(id_emp)
            if exito:
                self.view.mostrar_mensaje("Empleado eliminado exitosamente.")
            else:
                self.view.mostrar_mensaje("Error al eliminar en la base de datos.")
        else:
            self.view.mostrar_mensaje("Operación cancelada.")

    def imprimir_empleado(self) -> None:
        id_emp = self.view.solicitar_id()
        empleado = EmpleadoDAO.obtener_por_id(id_emp)
        if empleado:
            self.view.mostrar_empleado(empleado)
        else:
            self.view.mostrar_mensaje("Empleado no encontrado.")

    def imprimir_empleados(self) -> None:
        empleados = EmpleadoDAO.obtener_todos()
        self.view.mostrar_lista_empleados(empleados)