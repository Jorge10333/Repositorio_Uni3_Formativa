import hashlib  # Importa la librería para generar resúmenes criptográficos SHA-256
import hmac     # Importa la librería para comparar hashes en tiempo constante de forma segura
import re       # Importa expresiones regulares para validar formatos de texto


class Usuario:  # Define el modelo de dominio que representa una cuenta de usuario del sistema
    """
    Modelo de Dominio para la entidad Usuario (Autenticación y Cuentas).
    """
    ROLES: set[str] = {"Administrador", "Gerente", "Empleado", "Operador"}  # Conjunto de roles permitidos

    def __init__(  # Constructor de la clase Usuario
        self,
        nombre_usuario: str,       # Nombre de acceso del usuario
        contrasena_hash: str,      # Hash SHA-256 de la contraseña (64 caracteres hexadecimales)
        rol: str = "Empleado",     # Rol asignado dentro del sistema
        id_empleado: int | None = None,  # ID del empleado vinculado (opcional)
        id_usuario: int | None = None    # ID autoincremental de la base de datos (opcional al crear)
    ):
        self.id_usuario = id_usuario  # Asigna el identificador único del usuario
        self.nombre_usuario = nombre_usuario  # Llama al setter nombre_usuario para validar el formato
        self.contrasena_hash = contrasena_hash  # Llama al setter contrasena_hash para validar el hash SHA-256
        self.rol = rol  # Llama al setter rol para validar que sea un rol permitido
        self.id_empleado = id_empleado  # Asigna la referencia al empleado asociado

    @property  # Define el getter de nombre_usuario
    def nombre_usuario(self) -> str:
        return self._nombre_usuario  # Retorna el atributo privado _nombre_usuario

    @nombre_usuario.setter  # Define el setter de nombre_usuario con validaciones defensivas
    def nombre_usuario(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():  # Verifica que no sea nulo ni una cadena vacía
            raise ValueError("El nombre de usuario no puede estar vacío.")  # Lanza error si está vacío
        limpio = valor.strip().lower()  # Elimina espacios extremos y convierte a minúsculas
        if len(limpio) < 3:  # Exige una longitud mínima de 3 caracteres
            raise ValueError("El nombre de usuario debe tener al menos 3 caracteres.")  # Lanza error si es muy corto
        if not re.match(r"^[a-zA-Z0-9_.-]+$", limpio):  # Valida que solo tenga letras, números, puntos o guiones
            raise ValueError("El nombre de usuario contiene caracteres no permitidos.")  # Rechaza símbolos raros
        self._nombre_usuario = limpio  # Guarda el nombre de usuario ya validado y limpio

    @property  # Define el getter de contrasena_hash
    def contrasena_hash(self) -> str:
        return self._contrasena_hash  # Retorna el hash SHA-256 almacenado

    @contrasena_hash.setter  # Define el setter que impide almacenar contraseñas sin encriptar
    def contrasena_hash(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():  # Comprueba que el hash no esté vacío
            raise ValueError("El hash de la contraseña no puede estar vacío.")  # Rechaza valores vacíos
        limpio = valor.strip().lower()  # Limpia espacios y normaliza a minúsculas
        if len(limpio) != 64 or not re.match(r"^[a-f0-9]{64}$", limpio):  # Exige exactamente 64 caracteres hexadecimales
            raise ValueError("La credencial debe almacenarse como un hash SHA-256 válido.")  # Impide guardar texto plano
        self._contrasena_hash = limpio  # Guarda el hash validado en el atributo privado

    @property  # Define el getter de rol
    def rol(self) -> str:
        return self._rol  # Retorna el rol del usuario

    @rol.setter  # Define el setter de rol
    def rol(self, valor: str) -> None:
        if not isinstance(valor, str) or not valor.strip():  # Verifica que el rol no venga vacío
            raise ValueError("El rol no puede estar vacío.")  # Lanza error si está vacío
        rol_limpio = valor.strip().title()  # Elimina espacios y capitaliza la primera letra
        if rol_limpio not in self.ROLES:  # Verifica que el rol esté dentro del conjunto permitido
            opciones = ", ".join(sorted(self.ROLES))  # Prepara texto con los roles válidos
            raise ValueError(f"Rol '{valor}' no válido. Opciones permitidas: {opciones}.")  # Rechaza roles desconocidos
        self._rol = rol_limpio  # Guarda el rol validado

    @staticmethod  # Método estático que no requiere tener una instancia previa de Usuario
    def encriptar_credencial(clave_plana: str) -> str:
        if not isinstance(clave_plana, str) or not clave_plana.strip():  # Verifica que la clave no esté vacía
            raise ValueError("La contraseña no puede estar vacía ni contener solo espacios.")  # Rechaza claves vacías
        clave_limpia = clave_plana.strip()  # Quita espacios al inicio y al final
        if len(clave_limpia) < 4:  # Exige al menos 4 caracteres para la contraseña
            raise ValueError("La contraseña debe tener al menos 4 caracteres.")  # Lanza error si es demasiado corta
        return hashlib.sha256(clave_limpia.encode("utf-8")).hexdigest()  # Convierte a bytes, aplica SHA-256 y retorna hex

    @staticmethod  # Método estático para validar el formato de las credenciales antes de consultar la BD
    def validar_credenciales_ingreso(nombre_usuario: str, clave_plana: str) -> tuple[bool, str]:
        if not isinstance(nombre_usuario, str) or not nombre_usuario.strip():  # Valida que el usuario no esté vacío
            return (False, "El campo 'Usuario' no puede estar vacío.")  # Retorna falso y el motivo
        if not isinstance(clave_plana, str) or not clave_plana.strip():  # Valida que la contraseña no esté vacía
            return (False, "El campo 'Contraseña' no puede estar vacío.")  # Retorna falso y el motivo

        user_limpio = nombre_usuario.strip()  # Limpia espacios del usuario
        clave_limpia = clave_plana.strip()  # Limpia espacios de la contraseña

        if len(user_limpio) < 3:  # Verifica longitud mínima del usuario
            return (False, "El nombre de usuario debe tener al menos 3 caracteres.")  # Retorna falso
        if not re.match(r"^[a-zA-Z0-9_.-]+$", user_limpio):  # Verifica caracteres permitidos en el usuario
            return (False, "El nombre de usuario contiene caracteres no permitidos.")  # Retorna falso
        if len(clave_limpia) < 4:  # Verifica longitud mínima de la contraseña
            return (False, "La contraseña debe tener al menos 4 caracteres.")  # Retorna falso

        return (True, "Formato de credenciales válido.")  # Indica que ambos campos pasaron la validación

    def verificar_credencial(self, clave_ingresada: str) -> bool:  # Método que valida la clave ingresada en el login
        if not isinstance(clave_ingresada, str) or not clave_ingresada.strip():  # Rechaza entradas vacías
            return False  # Retorna falso inmediatamente
        try:  # Protege el cálculo del hash contra errores de longitud
            hash_ingresado = self.encriptar_credencial(clave_ingresada)  # Encripta la clave que escribió el usuario
            return hmac.compare_digest(self._contrasena_hash, hash_ingresado)  # Compara ambos hashes de forma segura
        except ValueError:  # Si la clave no cumple el formato mínimo
            return False  # Deniega la verificación

    def __str__(self) -> str:  # Representación en texto legible del objeto Usuario
        id_str = self.id_usuario if self.id_usuario is not None else "Sin asignar"  # Formatea el ID si existe
        emp_str = self.id_empleado if self.id_empleado is not None else "Sin empleado"  # Formatea el ID de empleado
        hash_resumen = f"{self.contrasena_hash[:12]}...{self.contrasena_hash[-6:]}"  # Muestra solo inicio y fin del hash
        return (
            f"Usuario [ID: {id_str}] | Username: {self.nombre_usuario} | "
            f"Rol: {self.rol} | Empleado ID: {emp_str} | Hash SHA-256: {hash_resumen}"
        )  # Retorna la ficha formateada

    def __repr__(self) -> str:  # Representación técnica para depuración
        return f"Usuario(id_usuario={self.id_usuario}, nombre_usuario='{self.nombre_usuario}', rol='{self.rol}')"