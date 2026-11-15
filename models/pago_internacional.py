import math  # Valida números finitos (rechaza nan e inf)
import re  # Valida códigos ISO de 3 letras para divisas
from datetime import datetime  # Valida formato y vigencia de la fecha de tasa
from decimal import Decimal, ROUND_HALF_UP  # Cálculo financiero exacto sin errores de coma flotante


class PagoInternacional:  # Modelo de pagos internacionales con aritmética Decimal
    MONTO_MAX = 1_000_000.0  # Límite superior permitido por operación
    MONEDAS_SIN_DECIMALES = {"CLP", "JPY", "KRW"}  # Divisas que se redondean a entero

    def __init__(
        self,
        pais_proyecto: str,
        moneda_origen: str,
        moneda_destino: str,
        monto_base: float,
        tasa_cambio: float,
        monto_convertido: float | None = None,
        fecha_tasa: str = "",
        origen: str = "API",
        fecha_registro: str | None = None,
        id_empleado: int | None = None,
        id_proyecto: int | None = None,
        id_usuario: int | None = None,
        id_pago: int | None = None,
    ):
        self.id_pago = id_pago
        self.pais_proyecto = pais_proyecto
        self.moneda_origen = moneda_origen
        self.moneda_destino = moneda_destino
        self.monto_base = monto_base
        self.tasa_cambio = tasa_cambio
        self.origen = origen if origen in ("API", "contingencia") else "API"
        self.fecha_tasa = fecha_tasa
        self.fecha_registro = fecha_registro or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.id_empleado = id_empleado
        self.id_proyecto = id_proyecto
        self.id_usuario = id_usuario

        # Calcula el monto final con precisión decimal según la moneda destino
        if monto_convertido is not None:
            self.monto_convertido = float(monto_convertido)
        else:
            cuanto = Decimal("1") if self._moneda_destino in self.MONEDAS_SIN_DECIMALES else Decimal("0.01")
            total = (Decimal(str(self._monto_base)) * Decimal(str(self._tasa_cambio))).quantize(
                cuanto, rounding=ROUND_HALF_UP
            )
            self.monto_convertido = float(total)

    @property
    def pais_proyecto(self) -> str:
        return self._pais_proyecto

    @pais_proyecto.setter
    def pais_proyecto(self, valor: str) -> None:
        if not isinstance(valor, str) or not (2 <= len(valor.strip()) <= 60):
            raise ValueError("El país del proyecto debe tener entre 2 y 60 caracteres.")
        self._pais_proyecto = valor.strip().title()

    @property
    def moneda_origen(self) -> str:
        return self._moneda_origen

    @moneda_origen.setter
    def moneda_origen(self, valor: str) -> None:
        if not isinstance(valor, str) or not re.fullmatch(r"[A-Za-z]{3}", valor.strip()):
            raise ValueError("La moneda de origen debe ser un código ISO de 3 letras (ej. USD).")
        self._moneda_origen = valor.strip().upper()

    @property
    def moneda_destino(self) -> str:
        return self._moneda_destino

    @moneda_destino.setter
    def moneda_destino(self, valor: str) -> None:
        if not isinstance(valor, str) or not re.fullmatch(r"[A-Za-z]{3}", valor.strip()):
            raise ValueError("La moneda de destino debe ser un código ISO de 3 letras (ej. CLP).")
        self._moneda_destino = valor.strip().upper()

    @property
    def monto_base(self) -> float:
        return self._monto_base

    @monto_base.setter
    def monto_base(self, valor: float | int) -> None:
        if (
            isinstance(valor, bool)
            or not isinstance(valor, (int, float))
            or not math.isfinite(valor)
            or not (0 < float(valor) <= self.MONTO_MAX)
        ):
            raise ValueError(f"El monto base debe ser un número finito mayor a 0 y hasta {self.MONTO_MAX:,.0f}.")
        self._monto_base = float(valor)

    @property
    def tasa_cambio(self) -> float:
        return self._tasa_cambio

    @tasa_cambio.setter
    def tasa_cambio(self, valor: float | int) -> None:
        if isinstance(valor, bool) or not isinstance(valor, (int, float)) or not math.isfinite(valor) or float(valor) <= 0:
            raise ValueError("La tasa de cambio debe ser un número finito mayor a 0.")
        self._tasa_cambio = float(valor)

    @property
    def fecha_tasa(self) -> str:
        return self._fecha_tasa

    @fecha_tasa.setter
    def fecha_tasa(self, valor: str) -> None:
        if not valor:
            self._fecha_tasa = ""
            return
        try:
            fecha_dt = datetime.strptime(valor.strip(), "%Y-%m-%d").date()
            if fecha_dt > datetime.now().date():
                raise ValueError("La fecha de la tasa no puede ser futura.")
            self._fecha_tasa = valor.strip()
        except ValueError as e:
            raise ValueError("La fecha de la tasa debe tener formato válido AAAA-MM-DD.") from e

    def __str__(self) -> str:
        emp_str = f"Emp #{self.id_empleado}" if self.id_empleado else "Sin empleado"
        proy_str = f"Proy #{self.id_proyecto}" if self.id_proyecto else "Sin proyecto"
        fecha_txt = self.fecha_tasa or "Sin fecha oficial"
        return (
            f"Pago #{self.id_pago or 'Nuevo'} [{self.origen}] | País: {self.pais_proyecto} ({emp_str} / {proy_str}) | "
            f"{self.monto_base:,.2f} {self.moneda_origen} -> {self.monto_convertido:,.2f} {self.moneda_destino} "
            f"(Tasa: {self.tasa_cambio:.4f} del {fecha_txt})"
        )