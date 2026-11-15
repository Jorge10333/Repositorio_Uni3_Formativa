import getpass  # Lee contraseñas ocultas en consola al crear el administrador inicial
import logging  # Registra errores de SQLite en logs/ecotech.log
import sqlite3  # Excepciones de base de datos
from datetime import datetime, timedelta  # Calcula la hora de desbloqueo tras fallos de login
from config.database import Database  # Singleton de conexión SQLite
from config.settings import Settings  # Lee límite de intentos y minutos de bloqueo
from .usuario import Usuario

log = logging.getLogger(__name__)


class UsuarioDAO:  # Administra operaciones SQL y bloqueo persistente para Usuario
    @staticmethod
    def _mapear(fila: sqlite3.Row) -> Usuario:  # Convierte una fila SQLite en objeto Usuario
        return Usuario(
            nombre_usuario=fila["nombreUsuario"],
            contrasena_hash=fila["clave_hash"],
            rol=fila["rol"],
            id_empleado=fila["id_empleado"],
            id_usuario=fila["idUsuario"],
            intentos_fallidos=fila["intentos_fallidos"],
            bloqueado_hasta=fila["bloqueado_hasta"],
        )

    @staticmethod
    def crear(usuario: Usuario) -> bool:  # Inserta un usuario nuevo usando consulta parametrizada
        conn = Database().get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO usuario (nombreUsuario, clave_hash, rol, intentos_fallidos, bloqueado_hasta, id_empleado)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    usuario.nombre_usuario,
                    usuario.contrasena_hash,
                    usuario.rol,
                    usuario.intentos_fallidos,
                    usuario.bloqueado_hasta,
                    usuario.id_empleado,
                ),
            )
            conn.commit()
            usuario.id_usuario = cursor.lastrowid
            return True
        except sqlite3.Error as e:
            log.error("Error al crear usuario '%s': %s", usuario.nombre_usuario, e)
            return False
        finally:
            conn.close()

    @classmethod
    def obtener_por_username(cls, nombre_usuario: str) -> Usuario | None:
        if not isinstance(nombre_usuario, str) or not nombre_usuario.strip():
            return None
        conn = Database().get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM usuario WHERE nombreUsuario = ?",
                (nombre_usuario.strip().lower(),),
            )
            fila = cursor.fetchone()
            return cls._mapear(fila) if fila else None
        except sqlite3.Error as e:
            log.error("Error al buscar usuario por username: %s", e)
            return None
        finally:
            conn.close()

    @classmethod
    def obtener_por_id(cls, id_usuario: int) -> Usuario | None:
        conn = Database().get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuario WHERE idUsuario = ?", (id_usuario,))
            fila = cursor.fetchone()
            return cls._mapear(fila) if fila else None
        except sqlite3.Error as e:
            log.error("Error al obtener usuario por ID %s: %s", id_usuario, e)
            return None
        finally:
            conn.close()

    @classmethod
    def obtener_todos(cls) -> list[Usuario]:
        conn = Database().get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM usuario ORDER BY idUsuario ASC")
            return [cls._mapear(f) for f in cursor.fetchall()]
        except sqlite3.Error as e:
            log.error("Error al listar usuarios: %s", e)
            return []
        finally:
            conn.close()

    @staticmethod
    def registrar_intento_fallido(usuario: Usuario) -> tuple[int, bool]:  # Guarda fallos y bloqueo en BD
        nuevos_intentos = usuario.intentos_fallidos + 1
        bloqueado_hasta = None
        bloqueado = False

        if nuevos_intentos >= Settings.MAX_LOGIN_ATTEMPTS:  # Activa bloqueo si alcanzó el límite
            bloqueado = True
            bloqueado_hasta = (
                datetime.now() + timedelta(minutes=Settings.LOCKOUT_MINUTES)
            ).isoformat(timespec="seconds")

        conn = Database().get_connection()
        try:
            conn.execute(
                "UPDATE usuario SET intentos_fallidos = ?, bloqueado_hasta = ? WHERE idUsuario = ?",
                (nuevos_intentos, bloqueado_hasta, usuario.id_usuario),
            )
            conn.commit()
            usuario.intentos_fallidos = nuevos_intentos
            usuario.bloqueado_hasta = bloqueado_hasta
        except sqlite3.Error as e:
            log.error("Error al actualizar intentos fallidos: %s", e)
        finally:
            conn.close()
        return (nuevos_intentos, bloqueado)

    @staticmethod
    def reiniciar_intentos(usuario: Usuario) -> None:  # Limpia fallos tras login correcto
        conn = Database().get_connection()
        try:
            conn.execute(
                "UPDATE usuario SET intentos_fallidos = 0, bloqueado_hasta = NULL WHERE idUsuario = ?",
                (usuario.id_usuario,),
            )
            conn.commit()
            usuario.intentos_fallidos = 0
            usuario.bloqueado_hasta = None
        except sqlite3.Error as e:
            log.error("Error al reiniciar intentos fallidos: %s", e)
        finally:
            conn.close()

    @staticmethod
    def eliminar(id_usuario: int) -> bool:
        conn = Database().get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuario WHERE idUsuario = ?", (id_usuario,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            log.error("Error al eliminar usuario ID %s: %s", id_usuario, e)
            return False
        finally:
            conn.close()

    @classmethod
    def inicializar_admin(cls) -> None:  # Pide crear el primer admin por consola si la tabla está vacía
        if cls.obtener_todos():
            return  # Si ya existe al menos un usuario, no hace nada

        print("\n" + "=" * 60)
        print("  PRIMER ARRANQUE: CONFIGURACIÓN DE ADMINISTRADOR INICIAL")
        print("=" * 60)
        while True:
            try:
                sugerido = Settings.ADMIN_INITIAL_USER
                user_in = input(f"Usuario administrador (Enter para '{sugerido}'): ").strip() or sugerido
                clave = getpass.getpass("Contraseña (8-128 caracteres, letras y números): ")
                confirmacion = getpass.getpass("Repita la contraseña: ")
                if clave != confirmacion:
                    print("[ERROR] Las contraseñas no coinciden. Intente nuevamente.\n")
                    continue
                hash_scrypt = Usuario.encriptar_credencial(clave)  # Encripta con scrypt antes de guardar
                admin = Usuario(user_in, hash_scrypt, "Administrador")
                if cls.crear(admin):
                    print(f"[OK] Administrador '{admin.nombre_usuario}' configurado con scrypt.\n")
                    return
                print("[ERROR] No se pudo guardar el administrador en la base de datos.\n")
            except ValueError as e:
                print(f"[ERROR] {e}\n")