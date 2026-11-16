import hashlib  # Provee el algoritmo criptográfico scrypt
import hmac  # Permite comparar hashes en tiempo constante (evita ataques de tiempo)
import os  # Genera bytes aleatorios seguros para la sal de cada usuario
import re  # Valida formatos de usuario, contraseña y hash mediante expresiones regulares
from datetime import datetime  # Controla la fecha y hora de vencimiento de bloqueos


class Usuario:  # Modelo de dominio para la entidad Usuario con hash scrypt con sal
    ROLES: set[str] = {"Administrador", "Gerente", "Empleado", "Operador"}  # Roles válidos del sistema
    SCRYPT_PARAMS = dict(n=2**14, r=8, p=1, dklen=32)  # Parámetros recomendados de costo para scrypt

    def __init__(
        self,
        nombre_usuario: str,
        contrasena_hash: str,
        rol: str = "Empleado",
        id_empleado: int | None = None,
        id_usuario: int | None = None,
        intentos_fallidos: int = 0,
        bloqueado_hasta: str | None = None,
    ):
        self.id_usuario = id_usuario  # ID autoincremental asignado por SQLite
        self.nombre_usuario = nombre_usuario  # Valida mediante setter
        self.contrasena_hash = contrasena_hash  # Valida mediante setter que sea hash scrypt
        self.rol = rol  # Valida mediante setter
        self.id_empleado = id_empleado  # ID del empleado asociado (opcional)
        self.intentos_fallidos = int(intentos_fallidos or 0)  # Contador de fallos consecutivos
        self.bloqueado_hasta = bloqueado_hasta  # Marca ISO de cuándo termina el bloqueo

    @property
    def nombre_usuario(self) -> str:
        return self._nombre_usuario

    @nombre_usuario.setter
    def nombre_usuario(self, valor: str) -> None:  # Valida largo (3-30) y caracteres seguros
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El nombre de usuario no puede estar vacío.")
        limpio = valor.strip().lower()  # Normaliza a minúsculas
        if not (3 <= len(limpio) <= 30):
            raise ValueError("El usuario debe tener entre 3 y 30 caracteres.")
        if not re.fullmatch(r"[a-z0-9_.-]+", limpio):
            raise ValueError("El usuario solo permite letras, números, puntos y guiones.")
        self._nombre_usuario = limpio

    @property
    def contrasena_hash(self) -> str:
        return self._contrasena_hash

    @contrasena_hash.setter
    def contrasena_hash(self, valor: str) -> None:  # Rechaza claves en texto plano o SHA-256 sin sal
        if not isinstance(valor, str) or not re.fullmatch(r"scrypt\$[a-f0-9]{32}\$[a-f0-9]{64}", valor):
            raise ValueError("La credencial debe almacenarse como hash scrypt con sal.")
        self._contrasena_hash = valor

    @property
    def rol(self) -> str:
        return self._rol

    @rol.setter
    def rol(self, valor: str) -> None:  # Asegura que el rol esté dentro del catálogo permitido
        if not isinstance(valor, str) or not valor.strip():
            raise ValueError("El rol no puede estar vacío.")
        rol_limpio = valor.strip().title()
        if rol_limpio not in self.ROLES:
            opciones = ", ".join(sorted(self.ROLES))
            raise ValueError(f"Rol no válido. Opciones permitidas: {opciones}.")
        self._rol = rol_limpio

    @staticmethod
    def validar_politica_clave(clave: str) -> None:  # Exige 8-128 caracteres mezclando letras y números
        if not isinstance(clave, str) or not clave.strip():  # No hace .strip() para respetar espacios reales
            raise ValueError("La contraseña no puede estar vacía ni ser solo espacios.")
        if not (8 <= len(clave) <= 128):
            raise ValueError("La contraseña debe tener entre 8 y 128 caracteres.")
        if not (re.search(r"[A-Za-z]", clave) and re.search(r"\d", clave)):
            raise ValueError("La contraseña debe incluir al menos una letra y un número.")

    @classmethod
    def encriptar_credencial(cls, clave_plana: str) -> str:  # Genera hash scrypt con sal aleatoria de 16 bytes
        cls.validar_politica_clave(clave_plana)
        sal = os.urandom(16)  # Sal única por cada usuario
        digest = hashlib.scrypt(clave_plana.encode("utf-8"), salt=sal, **cls.SCRYPT_PARAMS)
        return f"scrypt${sal.hex()}${digest.hex()}"  # Empaqueta algoritmo, sal y hash en un solo texto

    @staticmethod
    def validar_credenciales_ingreso(nombre_usuario: str, clave_plana: str) -> tuple[bool, str]:
        if not isinstance(nombre_usuario, str) or not nombre_usuario.strip():
            return (False, "El campo 'Usuario' no puede estar vacío.")
        if not isinstance(clave_plana, str) or not clave_plana.strip():
            return (False, "El campo 'Contraseña' no puede estar vacío.")

        user_limpio = nombre_usuario.strip().lower()
        if not (3 <= len(user_limpio) <= 30) or not re.fullmatch(r"[a-z0-9_.-]+", user_limpio):
            return (False, "Formato de usuario inválido (3 a 30 caracteres).")
        if not (1 <= len(clave_plana) <= 128):  # Limita el largo máximo para evitar sobrecarga de CPU
            return (False, "Longitud de contraseña fuera de rango.")
        return (True, "Formato válido.")

    def verificar_credencial(self, clave_ingresada: str) -> bool:  # Verifica clave contra el hash guardado
        if not isinstance(clave_ingresada, str) or not (1 <= len(clave_ingresada) <= 128):
            return False
        try:
            _, sal_hex, hash_hex = self._contrasena_hash.split("$")  # Separa sal y digest almacenados
            calculado = hashlib.scrypt(
                clave_ingresada.encode("utf-8"),
                salt=bytes.fromhex(sal_hex),
                **self.SCRYPT_PARAMS,
            )
            return hmac.compare_digest(calculado.hex(), hash_hex)  # Compara en tiempo constante
        except (ValueError, TypeError):
            return False

    def esta_bloqueado(self) -> tuple[bool, str]:  # Comprueba si el bloqueo temporal sigue activo
        if not self.bloqueado_hasta:
            return (False, "")
        try:
            limite = datetime.fromisoformat(self.bloqueado_hasta)
            ahora = datetime.now()
            if ahora < limite:
                segundos = int((limite - ahora).total_seconds())
                return (True, f"Cuenta bloqueada temporalmente. Intente en {segundos} segundos.")
        except ValueError:
            pass
        return (False, "")

    def __str__(self) -> str:
        id_str = self.id_usuario if self.id_usuario is not None else "Sin asignar"
        emp_str = self.id_empleado if self.id_empleado is not None else "Sin empleado"
        partes = self.contrasena_hash.split("$")
        resumen = f"scrypt${partes[1][:6]}...${partes[2][:8]}..."  # Muestra solo prefijo del hash por seguridad
        return (
            f"Usuario [ID: {id_str}] | Username: {self.nombre_usuario} | "
            f"Rol: {self.rol} | Empleado ID: {emp_str} | Hash: {resumen}"
        )