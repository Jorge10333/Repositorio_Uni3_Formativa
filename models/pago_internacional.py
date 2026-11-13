import re  # Importa expresiones regulares para validar códigos de moneda ISO (ej. USD, CLP, EUR)
from datetime import datetime  # Importa datetime para sellar la fecha exacta del cálculo


class PagoInternacional:  # Define el modelo de dominio para un pago ajustado a moneda extranjera
    """
    Modelo de Dominio que representa el cálculo y respaldo de un pago internacional
    utilizando el tipo de cambio obtenido desde Frankfurter API.
    """
    def __init__(  # Constructor de la clase PagoInternacional
        self,
        pais_proyecto: str,                 # País donde se ejecuta el proyecto (ej. Chile, Brasil, España)
        moneda_origen: str,                 # Código ISO de la moneda base (ej. USD)
        moneda_destino: str,                # Código ISO de la moneda del país destino (ej. CLP, EUR, BRL)
        monto_base: float,                  # Monto original a pagar en moneda_origen
        tasa_cambio: float,                 # Tasa de conversión obtenida desde la API externa
        monto_convertido: float | None = None,  # Resultado final (si es None, se calcula automáticamente)
        fecha_tasa: str | None = None,      # Fecha oficial de publicación de la tasa económica
        fecha_registro: str | None = None,  # Fecha y hora local en que se registró el pago
        id_empleado: int | None = None,     # ID del trabajador beneficiario (opcional)
        id_proyecto: int | None = None,     # ID del proyecto asociado (opcional)
        id_usuario: int | None = None,      # ID del usuario autenticado que realizó el cálculo
        id_pago: int | None = None          # ID autoincremental generado por SQLite
    ):
        self.id_pago = id_pago  # Asigna el identificador único del registro
        self.pais_proyecto = pais_proyecto  # Llama al setter pais_proyecto para validar el texto
        self.moneda_origen = moneda_origen  # Llama al setter moneda_origen para validar formato ISO de 3 letras
        self.moneda_destino = moneda_destino  # Llama al setter moneda_destino para validar formato ISO de 3 letras
        self.monto_base = monto_base  # Llama al setter monto_base para validar que sea mayor a cero
        self.tasa_cambio = tasa_cambio  # Llama al setter tasa_cambio para validar que sea mayor a cero
        # Si no se entrega el monto convertido, lo calcula multiplicando monto_base * tasa_cambio
        self.monto_convertido = (
            round(float(monto_convertido), 2)
            if monto_convertido is not None
            else round(self._monto_base * self._tasa_cambio, 2)
        )  # Redondea el total convertido a 2 decimales
        self.fecha_tasa = fecha_tasa or datetime.now().strftime("%Y-%m-%d")  # Fecha de vigencia de la tasa
        self.fecha_registro = fecha_registro or datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Marca de tiempo local
        self.id_empleado = id_empleado  # Asigna referencia al empleado
        self.id_proyecto = id_proyecto  # Asigna referencia al proyecto
        self.id_usuario = id_usuario  # Asigna referencia al operador del sistema

    @property  # Getter de pais_proyecto
    def pais_proyecto(self) -> str:
        return self._pais_proyecto  # Retorna el nombre del país

    @pais_proyecto.setter  # Setter de pais_proyecto con validación
    def pais_proyecto(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():  # Verifica que no esté vacío
            raise ValueError("El país del proyecto no puede estar vacío.")  # Rechaza valores vacíos
        self._pais_proyecto = valor.strip().title()  # Limpia espacios y capitaliza cada palabra

    @property  # Getter de moneda_origen
    def moneda_origen(self) -> str:
        return self._moneda_origen  # Retorna el código ISO de origen

    @moneda_origen.setter  # Setter de moneda_origen
    def moneda_origen(self, valor: str) -> None:
        if not isinstance(valor, str) or not re.fullmatch(r"[A-Za-z]{3}", valor.strip()):  # Exige 3 letras ISO
            raise ValueError("La moneda de origen debe ser un código ISO de 3 letras (ej. USD, EUR).")
        self._moneda_origen = valor.strip().upper()  # Guarda en mayúsculas estándar (ej. 'USD')

    @property  # Getter de moneda_destino
    def moneda_destino(self) -> str:
        return self._moneda_destino  # Retorna el código ISO de destino

    @moneda_destino.setter  # Setter de moneda_destino
    def moneda_destino(self, valor: str) -> None:
        if not isinstance(valor, str) or not re.fullmatch(r"[A-Za-z]{3}", valor.strip()):  # Exige 3 letras ISO
            raise ValueError("La moneda de destino debe ser un código ISO de 3 letras (ej. CLP, BRL, MXN).")
        self._moneda_destino = valor.strip().upper()  # Guarda en mayúsculas estándar (ej. 'CLP')

    @property  # Getter de monto_base
    def monto_base(self) -> float:
        return self._monto_base  # Retorna el monto base

    @monto_base.setter  # Setter de monto_base
    def monto_base(self, valor: float | int) -> None:
        if not isinstance(valor, (int, float)) or float(valor) <= 0:  # Impide montos negativos o iguales a cero
            raise ValueError("El monto base debe ser un número mayor a 0.")
        self._monto_base = float(valor)  # Almacena como decimal

    @property  # Getter de tasa_cambio
    def tasa_cambio(self) -> float:
        return self._tasa_cambio  # Retorna el tipo de cambio aplicado

    @tasa_cambio.setter  # Setter de tasa_cambio
    def tasa_cambio(self, valor: float | int) -> None:
        if not isinstance(valor, (int, float)) or float(valor) <= 0:  # Impide tasas inválidas <= 0
            raise ValueError("La tasa de cambio debe ser un valor numérico mayor a 0.")
        self._tasa_cambio = float(valor)  # Almacena como decimal

    def __str__(self) -> str:  # Representación en texto legible para listados administrativos
        emp_str = f"Emp #{self.id_empleado}" if self.id_empleado else "Sin empleado"  # Formatea empleado
        proy_str = f"Proy #{self.id_proyecto}" if self.id_proyecto else "Sin proyecto"  # Formatea proyecto
        return (
            f"Pago #{self.id_pago or 'Nuevo'} | País: {self.pais_proyecto} ({emp_str} / {proy_str}) | "
            f"{self.monto_base:,.2f} {self.moneda_origen} -> {self.monto_convertido:,.2f} {self.moneda_destino} "
            f"(Tasa: {self.tasa_cambio:.4f} del {self.fecha_tasa})"
        )  # Retorna ficha formateada del pago internacional