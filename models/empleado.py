from .departamento import Departamento

class Empleado:
    """
    Modelo DTO de la entidad Empleado.
    """
    def __init__(
        self,
        nombre: str,
        direccion: str,
        telefono: str,
        email: str,
        fecha_inicio: str,
        salario: float,
        departamento: Departamento | None = None,
        id_unico: int | None = None
    ):
        self.id_unico = id_unico
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email
        self.fecha_inicio = fecha_inicio
        self.salario = salario
        self.departamento = departamento

    @property
    def nombre(self) -> str:
        return self._nombre

    @nombre.setter
    def nombre(self, valor: str) -> None:
        # Validación de longitud mínima del nombre
        if not isinstance(valor, str) or len(valor.strip()) < 2:
            raise ValueError("El nombre debe tener al menos 2 caracteres.")
        self._nombre = valor.strip().title()

    @property
    def email(self) -> str:
        return self._email

    @email.setter
    def email(self, valor: str) -> None:
        # Validación básica de estructura de correo electrónico
        if "@" not in valor or "." not in valor:
            raise ValueError("El correo electrónico no es válido.")
        self._email = valor.strip().lower()

    @property
    def salario(self) -> float:
        return self._salario

    @salario.setter
    def salario(self, valor: float | int) -> None:
        # Evita valores negativos para el sueldo
        if not isinstance(valor, (int, float)) or valor < 0:
            raise ValueError("El salario debe ser un número positivo.")
        self._salario = float(valor)

    @property
    def departamento(self) -> Departamento | None:
        return self._departamento

    @departamento.setter
    def departamento(self, depto: Departamento | None) -> None:
        # Verifica que sea un objeto de la clase Departamento
        if depto is not None and not isinstance(depto, Departamento):
            raise TypeError("El departamento debe ser una instancia de la clase Departamento o None.")
        self._departamento = depto

    def __str__(self) -> str:
        id_str = self.id_unico if self.id_unico is not None else 'Sin asignar'
        depto_str = self.departamento.nombre if self.departamento else 'Ninguno'
        return f"Empleado [ID: {id_str}] | Nombre: {self.nombre} | Email: {self.email} | Salario: ${self.salario:,.2f} | Depto: {depto_str}"