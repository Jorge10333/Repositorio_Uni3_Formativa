class EmpleadoProyecto:
    def __init__(self, id_empleado: int, id_proyecto: int, id_empleado_proyecto: int | None = None):
        self.id_empleado_proyecto = id_empleado_proyecto
        self.id_empleado = id_empleado
        self.id_proyecto = id_proyecto