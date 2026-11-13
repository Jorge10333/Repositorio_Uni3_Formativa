import sqlite3  # Importa sqlite3 para capturar excepciones específicas de base de datos
from sqlite3 import Cursor  # Importa Cursor para anotación de tipos
from config.database import Database  # Importa la clase Singleton de conexión
from config.settings import Settings  # Importa la configuración para el administrador por defecto
from .usuario import Usuario  # Importa el modelo de dominio Usuario


class UsuarioDAO:  # Define el objeto de acceso a datos (DAO) para la tabla usuario
    """
    Data Access Object para la entidad Usuario.
    """
    @staticmethod  # Método estático para insertar un nuevo usuario en SQLite
    def crear(usuario: Usuario) -> bool:
        conn = Database().get_connection()  # Abre conexión con la base de datos
        try:  # Protege la inserción SQL contra errores de integridad o disco
            cursor: Cursor = conn.cursor()  # Obtiene el cursor para ejecutar comandos SQL
            # Ejecuta INSERT parametrizado (?) para evitar ataques de Inyección SQL (SQLi)
            cursor.execute(
                "INSERT INTO usuario (nombreUsuario, contraseñaHash, rol, id_empleado) VALUES (?, ?, ?, ?)",
                (usuario.nombre_usuario, usuario.contrasena_hash, usuario.rol, usuario.id_empleado)
            )  # Pasa los valores como tupla separada de la sentencia SQL
            conn.commit()  # Guarda los cambios en la base de datos
            usuario.id_usuario = cursor.lastrowid  # Asigna al objeto el ID autoincremental generado por SQLite
            return True  # Indica que el registro se guardó con éxito
        except sqlite3.IntegrityError:  # Captura error si el nombreUsuario ya existe (UNIQUE) o id_empleado no existe
            print(f"Error: El usuario '{usuario.nombre_usuario}' ya existe o el empleado asociado no es válido.")
            return False  # Retorna False indicando fallo controlado
        except sqlite3.Error as e:  # Captura cualquier otro error de SQLite
            print(f"Error al crear usuario en BD: {e}")
            return False  # Retorna False sin detener el programa
        finally:  # Se ejecuta siempre al finalizar
            conn.close()  # Cierra la conexión con la base de datos

    @staticmethod  # Método estático para buscar un usuario por su nombre de login
    def obtener_por_username(nombre_usuario: str) -> Usuario | None:
        if not isinstance(nombre_usuario, str) or not nombre_usuario.strip():  # Valida que no sea vacío
            return None  # Si está vacío, retorna None sin consultar la BD
        conn = Database().get_connection()  # Abre conexión a SQLite
        usuario = None  # Inicializa la variable de retorno en None
        try:  # Protege la consulta SELECT
            cursor: Cursor = conn.cursor()  # Crea el cursor
            cursor.execute(
                "SELECT * FROM usuario WHERE nombreUsuario = ?",  # Consulta parametrizada por nombreUsuario
                (nombre_usuario.strip().lower(),)  # Tupla de un elemento con el nombre normalizado
            )
            fila = cursor.fetchone()  # Obtiene la fila encontrada (o None si no existe)
            if fila:  # Si se encontró un registro en la base de datos
                usuario = Usuario(  # Reconstruye y retorna una instancia del modelo Usuario
                    nombre_usuario=fila["nombreUsuario"],
                    contrasena_hash=fila["contraseñaHash"],
                    rol=fila["rol"],
                    id_empleado=fila["id_empleado"],
                    id_usuario=fila["idUsuario"]
                )
        except sqlite3.Error as e:  # Captura errores de lectura SQL
            print(f"Error al buscar usuario: {e}")
        finally:
            conn.close()  # Cierra la conexión
        return usuario  # Retorna el objeto Usuario o None

    @staticmethod  # Método estático para buscar un usuario por su clave primaria idUsuario
    def obtener_por_id(id_usuario: int) -> Usuario | None:
        conn = Database().get_connection()  # Abre conexión
        usuario = None  # Inicializa el resultado en None
        try:
            cursor: Cursor = conn.cursor()  # Crea cursor
            cursor.execute("SELECT * FROM usuario WHERE idUsuario = ?", (id_usuario,))  # Consulta parametrizada
            fila = cursor.fetchone()  # Obtiene el registro
            if fila:  # Si existe el ID
                usuario = Usuario(  # Instancia el objeto Usuario con los datos de la fila
                    nombre_usuario=fila["nombreUsuario"],
                    contrasena_hash=fila["contraseñaHash"],
                    rol=fila["rol"],
                    id_empleado=fila["id_empleado"],
                    id_usuario=fila["idUsuario"]
                )
        except sqlite3.Error as e:
            print(f"Error al obtener usuario por ID: {e}")
        finally:
            conn.close()  # Cierra conexión
        return usuario  # Retorna el Usuario encontrado o None

    @staticmethod  # Método estático para listar todos los usuarios registrados
    def obtener_todos() -> list[Usuario]:
        conn = Database().get_connection()  # Abre conexión
        usuarios: list[Usuario] = []  # Crea una lista vacía para almacenar los objetos Usuario
        try:
            cursor: Cursor = conn.cursor()  # Crea cursor
            cursor.execute("SELECT * FROM usuario ORDER BY idUsuario ASC")  # Consulta todos ordenados por ID
            for fila in cursor.fetchall():  # Recorre cada fila devuelta por SQLite
                usuarios.append(  # Convierte cada fila en un objeto Usuario y lo agrega a la lista
                    Usuario(
                        nombre_usuario=fila["nombreUsuario"],
                        contrasena_hash=fila["contraseñaHash"],
                        rol=fila["rol"],
                        id_empleado=fila["id_empleado"],
                        id_usuario=fila["idUsuario"]
                    )
                )
        except sqlite3.Error as e:
            print(f"Error al obtener usuarios: {e}")
        finally:
            conn.close()  # Cierra conexión
        return usuarios  # Retorna la lista de usuarios

    @staticmethod  # Método estático para actualizar datos de un usuario existente
    def actualizar(usuario: Usuario) -> bool:
        if usuario.id_usuario is None:  # Verifica que el usuario tenga un ID asignado en BD
            return False  # No se puede actualizar un registro sin ID
        conn = Database().get_connection()  # Abre conexión
        try:
            cursor: Cursor = conn.cursor()  # Crea cursor
            cursor.execute(
                """
                UPDATE usuario
                SET nombreUsuario = ?, contraseñaHash = ?, rol = ?, id_empleado = ?
                WHERE idUsuario = ?
                """,
                (usuario.nombre_usuario, usuario.contrasena_hash, usuario.rol, usuario.id_empleado, usuario.id_usuario)
            )  # Ejecuta actualización parametrizada
            conn.commit()  # Guarda los cambios
            return cursor.rowcount > 0  # Retorna True si se modificó al menos una fila
        except sqlite3.Error as e:
            print(f"Error al actualizar usuario: {e}")
            return False
        finally:
            conn.close()  # Cierra conexión

    @staticmethod  # Método estático para eliminar una cuenta de usuario por su ID
    def eliminar(id_usuario: int) -> bool:
        conn = Database().get_connection()  # Abre conexión
        try:
            cursor: Cursor = conn.cursor()  # Crea cursor
            cursor.execute("DELETE FROM usuario WHERE idUsuario = ?", (id_usuario,))  # Ejecuta DELETE seguro
            conn.commit()  # Confirma la eliminación
            return cursor.rowcount > 0  # Retorna True si se eliminó el registro
        except sqlite3.Error as e:
            print(f"Error al eliminar usuario: {e}")
            return False
        finally:
            conn.close()  # Cierra conexión

    @classmethod  # Método de clase que crea el usuario administrador inicial si la tabla está vacía
    def inicializar_admin_por_defecto(cls) -> None:
        if not cls.obtener_todos():  # Verifica si no hay ningún usuario registrado en la base de datos
            try:  # Protege la creación del usuario semilla
                hash_inicial = Usuario.encriptar_credencial(Settings.ADMIN_INITIAL_CLAVE)  # Encripta la clave del .env
                admin_default = Usuario(  # Crea la instancia del administrador por defecto
                    nombre_usuario=Settings.ADMIN_INITIAL_USER,  # Toma el usuario desde Settings
                    contrasena_hash=hash_inicial,  # Asigna el hash SHA-256 generado
                    rol="Administrador",  # Asigna el rol de mayor privilegio
                    id_empleado=None  # No requiere estar vinculado a un empleado físico
                )
                cls.crear(admin_default)  # Inserta el administrador en SQLite
            except ValueError as e:  # Captura error si la configuración en .env es inválida
                print(f"Error al inicializar el administrador por defecto: {e}")