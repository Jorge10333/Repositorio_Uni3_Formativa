from datetime import datetime  # Importa datetime para generar la fecha y hora exacta de cada consulta


class ReporteClima:  # Define el modelo de dominio para un reporte meteorológico
    """
    Modelo de Dominio para representar los datos meteorológicos obtenidos desde Open-Meteo.
    """
    def __init__(  # Constructor de la clase ReporteClima
        self,
        ciudad: str,                     # Nombre de la ciudad consultada
        temperatura: float,              # Temperatura actual en grados Celsius
        pais: str = "No especificado",   # País al que pertenece la ciudad
        velocidad_viento: float = 0.0,   # Velocidad del viento en km/h
        fecha_consulta: str | None = None,  # Fecha y hora en que se realizó la consulta
        id_proyecto: int | None = None,  # ID del proyecto asociado (opcional)
        id_usuario: int | None = None,   # ID del usuario que realizó la consulta (opcional)
        id_reporte: int | None = None    # ID autoincremental de SQLite (opcional al crear)
    ):
        self.id_reporte = id_reporte  # Asigna el ID del reporte
        self.ciudad = ciudad  # Llama al setter ciudad para validar el nombre
        self.pais = pais  # Asigna el país
        self.temperatura = temperatura  # Llama al setter temperatura para validar que sea numérico
        self.velocidad_viento = float(velocidad_viento)  # Convierte la velocidad del viento a decimal
        self.fecha_consulta = fecha_consulta or datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Asigna fecha actual si no viene
        self.id_proyecto = id_proyecto  # Asigna el proyecto vinculado
        self.id_usuario = id_usuario  # Asigna el usuario que consultó

    @property  # Getter de ciudad
    def ciudad(self) -> str:
        return self._ciudad  # Retorna el nombre de la ciudad

    @ciudad.setter  # Setter de ciudad con validación
    def ciudad(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():  # Verifica que la ciudad no sea vacía
            raise ValueError("El nombre de la ciudad no puede estar vacío.")  # Lanza error si está vacía
        self._ciudad = valor.strip().title()  # Limpia espacios y formatea en Tipo Título

    @property  # Getter de temperatura
    def temperatura(self) -> float:
        return self._temperatura  # Retorna la temperatura en °C

    @temperatura.setter  # Setter de temperatura con validación numérica
    def temperatura(self, valor: float | int) -> None:
        if not isinstance(valor, (int, float)):  # Verifica que el valor sea entero o decimal
            raise ValueError("La temperatura debe ser un valor numérico.")  # Lanza error si no es número
        self._temperatura = float(valor)  # Guarda la temperatura como float

    def __str__(self) -> str:  # Formatea el reporte climático para mostrarlo en listados de consola
        proy_str = f"Proyecto #{self.id_proyecto}" if self.id_proyecto else "Consulta General"  # Indica si tiene proyecto
        return (
            f"Reporte #{self.id_reporte or 'Nuevo'} | {self.ciudad} ({self.pais}) | "
            f"Temp: {self.temperatura:.1f} °C | Viento: {self.velocidad_viento:.1f} km/h | "
            f"Destino: {proy_str} | Fecha: {self.fecha_consulta}"
        )  # Retorna la línea resumen del reporte