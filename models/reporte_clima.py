import math  # Valida que temperatura, humedad y viento sean números finitos
from datetime import datetime  # Genera marca de tiempo local cuando no se recibe una


def describir_clima(codigo: int) -> str:  # Traduce el código numérico WMO a descripción legible
    if codigo == 0:
        return "Despejado"
    if codigo in (1, 2, 3):
        return "Parcialmente nublado"
    if codigo in (45, 48):
        return "Niebla"
    if 51 <= codigo <= 57:
        return "Llovizna"
    if (61 <= codigo <= 67) or (80 <= codigo <= 82):
        return "Lluvia"
    if (71 <= codigo <= 77) or codigo in (85, 86):
        return "Nieve"
    if codigo >= 95:
        return "Tormenta"
    return "Sin descripción"


class ReporteClima:  # Modelo meteorológico con validación de rangos y recomendación operativa
    def __init__(
        self,
        ciudad: str,
        temperatura: float,
        pais: str = "No especificado",
        humedad: float = 0.0,
        codigo_clima: int = 0,
        descripcion_clima: str | None = None,
        velocidad_viento: float = 0.0,
        origen: str = "API",
        fecha_consulta: str | None = None,
        id_proyecto: int | None = None,
        id_usuario: int | None = None,
        id_reporte: int | None = None,
    ):
        self.id_reporte = id_reporte
        self.ciudad = ciudad  # Valida mediante setter
        self.pais = pais.strip() if isinstance(pais, str) and pais.strip() else "No especificado"
        self.temperatura = temperatura  # Valida rango -90 a 60 °C
        self.humedad = humedad  # Valida rango 0 a 100 %
        self.codigo_clima = int(codigo_clima)
        self.descripcion_clima = descripcion_clima or describir_clima(self.codigo_clima)
        self.velocidad_viento = velocidad_viento  # Valida >= 0 km/h
        self.origen = origen if origen in ("API", "contingencia") else "API"  # Diferencia fuente real de respaldo
        self.fecha_consulta = fecha_consulta or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.id_proyecto = id_proyecto
        self.id_usuario = id_usuario

    @property
    def ciudad(self) -> str:
        return self._ciudad

    @ciudad.setter
    def ciudad(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre de la ciudad no puede estar vacío.")
        self._ciudad = valor.strip()

    @property
    def temperatura(self) -> float:
        return self._temperatura

    @temperatura.setter
    def temperatura(self, valor: float | int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
            raise ValueError("La temperatura debe ser un número finito.")
        if not (-90.0 <= float(valor) <= 60.0):
            raise ValueError("Temperatura fuera de rango lógico (-90 °C a 60 °C).")
        self._temperatura = float(valor)

    @property
    def humedad(self) -> float:
        return self._humedad

    @humedad.setter
    def humedad(self, valor: float | int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
            raise ValueError("La humedad debe ser un número finito.")
        if not (0.0 <= float(valor) <= 100.0):
            raise ValueError("La humedad relativa debe estar entre 0% y 100%.")
        self._humedad = float(valor)

    @property
    def velocidad_viento(self) -> float:
        return self._velocidad_viento

    @velocidad_viento.setter
    def velocidad_viento(self, valor: float | int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor):
            raise ValueError("La velocidad del viento debe ser un número finito.")
        if float(valor) < 0:
            raise ValueError("La velocidad del viento no puede ser negativa.")
        self._velocidad_viento = float(valor)

    def evaluar_condiciones(self) -> tuple[str, str]:  # Apoya decisiones operativas en terreno
        if self.codigo_clima >= 95 or self.velocidad_viento >= 60:
            return ("Reprogramar", "Tormenta o viento extremo: suspender trabajo en terreno.")
        if self.velocidad_viento >= 40 or self.codigo_clima in range(61, 68) or self.codigo_clima in (80, 81, 82):
            return ("Precaución", "Lluvia o viento fuerte: limitar trabajos en altura y al aire libre.")
        if self.temperatura >= 35 or self.temperatura <= 0:
            return ("Precaución", "Temperatura extrema: aplicar medidas de seguridad laboral.")
        return ("Apto", "Condiciones normales para trabajar en terreno.")

    def __str__(self) -> str:
        proy_str = f"Proyecto #{self.id_proyecto}" if self.id_proyecto else "Consulta General"
        estado_op, _ = self.evaluar_condiciones()
        return (
            f"Reporte #{self.id_reporte or 'Nuevo'} [{self.origen}] | {self.ciudad} ({self.pais}) | "
            f"{self.descripcion_clima} | Temp: {self.temperatura:.1f}°C | Hum: {self.humedad:.0f}% | "
            f"Viento: {self.velocidad_viento:.1f} km/h | Decisión: {estado_op} | {proy_str} | {self.fecha_consulta}"
        )