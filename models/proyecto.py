class Proyecto:
    """
    Modelo DTO de la entidad Proyecto.
    """
    def __init__(self, nombre: str, descripcion: str, fecha_inicio: str, id_proyecto: int | None = None):
        self.id_proyecto = id_proyecto
        self.nombre = nombre
        self.descripcion = descripcion
        self.fecha_inicio = fecha_inicio

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        # Valida que el nombre del proyecto no esté vacío
        if not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ValueError("El nombre del proyecto es obligatorio.")
        self._nombre = valor.strip()

    def __str__(self) -> str:
        id_str = self.id_proyecto if self.id_proyecto is not None else 'Sin asignar'
        return f"Proyecto [ID: {id_str}] | Nombre: {self.nombre} | Fecha Inicio: {self.fecha_inicio}"