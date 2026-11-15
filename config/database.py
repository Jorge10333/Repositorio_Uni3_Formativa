import logging  # Registra fallos de base de datos en logs/ecotech.log
import sqlite3  # Motor SQLite incluido en Python
from sqlite3 import Connection, Cursor  # Tipos para claridad en firmas de métodos

log = logging.getLogger(__name__)  # Crea un logger identificado con el nombre de este archivo


class Database:  # Administra una única instancia de conexión a SQLite (Patrón Singleton)
    _instance = None  # Guarda la única instancia creada en memoria
    _db_path = "ecotech_solutions.db"  # Nombre de la db

    def __new__(cls):  # Controla la creación del objeto para devolver siempre el mismo
        if cls._instance is None:  # Solo crea la instancia la primera vez que se llama
            cls._instance = super(Database, cls).__new__(cls)  # Reserva memoria para la instancia
        return cls._instance  # Devuelve la instancia única

    def get_connection(self) -> Connection:  # Abre una conexión configurada con llaves foráneas
        try:  # Intenta abrir el archivo de base de datos
            conn = sqlite3.connect(self._db_path)  # Conecta con el archivo SQLite
            conn.row_factory = sqlite3.Row  # Permite leer columnas como diccionario (fila["nombre"])
            conn.execute("PRAGMA foreign_keys = ON;")  # Obliga a SQLite a respetar relaciones entre tablas
            return conn  # Entrega la conexión lista para usar
        except sqlite3.Error as e:  # Si falla la apertura del archivo .db
            log.error("Error al conectar con SQLite: %s", e)  # Guarda el error técnico en el log
            raise  # Propaga el fallo hacia arriba

    def init_db(self) -> None:  # Crea las 8 tablas del sistema si todavía no existen
        conn = None  # Inicializa la variable en None por si falla antes de conectar
        try:  # Ejecuta todas las sentencias DDL dentro de un bloque protegido
            conn = self.get_connection()  # Obtiene conexión activa
            cursor: Cursor = conn.cursor()  # Crea el cursor para ejecutar SQL

            # Tabla de departamentos de la empresa
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS departamento (
                    id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    id_gerente INTEGER,
                    FOREIGN KEY(id_gerente) REFERENCES empleado(idUnico) ON DELETE SET NULL
                )
            """)

            # Tabla principal de empleados
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS empleado (
                    idUnico INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    direccion TEXT,
                    telefono TEXT,
                    email TEXT NOT NULL,
                    fechaInicio TEXT NOT NULL,
                    salario REAL,
                    id_departamento INTEGER,
                    FOREIGN KEY(id_departamento) REFERENCES departamento(id_departamento) ON DELETE SET NULL
                )
            """)

            # Tabla de cuentas de usuario (clave_hash guarda scrypt y bloqueado_hasta persiste bloqueos)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS usuario (
                    idUsuario INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombreUsuario TEXT NOT NULL UNIQUE,
                    clave_hash TEXT NOT NULL,
                    rol TEXT NOT NULL,
                    intentos_fallidos INTEGER NOT NULL DEFAULT 0,
                    bloqueado_hasta TEXT,
                    id_empleado INTEGER,
                    FOREIGN KEY(id_empleado) REFERENCES empleado(idUnico) ON DELETE CASCADE
                )
            """)

            # Tabla de proyectos de EcoTech Solutions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS proyecto (
                    id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    fechaInicio TEXT NOT NULL
                )
            """)

            # Tabla intermedia muchos a muchos entre empleados y proyectos
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS empleado_proyecto (
                    id_empleado_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_empleado INTEGER NOT NULL,
                    id_proyecto INTEGER NOT NULL,
                    FOREIGN KEY(id_empleado) REFERENCES empleado(idUnico) ON DELETE CASCADE,
                    FOREIGN KEY(id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE,
                    UNIQUE(id_empleado, id_proyecto)
                )
            """)

            # Registro de horas trabajadas por empleado en cada proyecto
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS registro_tiempo (
                    id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                    fecha TEXT NOT NULL,
                    cantidadHoraTrabajada REAL NOT NULL,
                    descripcionTareaRealizada TEXT NOT NULL,
                    id_empleado INTEGER NOT NULL,
                    id_proyecto INTEGER NOT NULL,
                    FOREIGN KEY(id_empleado) REFERENCES empleado(idUnico) ON DELETE CASCADE,
                    FOREIGN KEY(id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE
                )
            """)

            # Historial de reportes climáticos con humedad, código WMO y origen ('API' o 'contingencia')
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS reporte_clima (
                    id_reporte INTEGER PRIMARY KEY AUTOINCREMENT,
                    ciudad TEXT NOT NULL,
                    pais TEXT,
                    temperatura REAL NOT NULL,
                    humedad REAL NOT NULL DEFAULT 0,
                    codigo_clima INTEGER NOT NULL DEFAULT 0,
                    descripcion_clima TEXT NOT NULL DEFAULT 'Sin descripción',
                    velocidad_viento REAL NOT NULL DEFAULT 0,
                    origen TEXT NOT NULL DEFAULT 'API',
                    fecha_consulta TEXT NOT NULL,
                    id_proyecto INTEGER,
                    id_usuario INTEGER,
                    FOREIGN KEY(id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE SET NULL,
                    FOREIGN KEY(id_usuario) REFERENCES usuario(idUsuario) ON DELETE SET NULL
                )
            """)

            # Historial de liquidaciones internacionales calculadas con Frankfurter API
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pago_internacional (
                    id_pago INTEGER PRIMARY KEY AUTOINCREMENT,
                    pais_proyecto TEXT NOT NULL,
                    moneda_origen TEXT NOT NULL,
                    moneda_destino TEXT NOT NULL,
                    monto_base REAL NOT NULL,
                    tasa_cambio REAL NOT NULL,
                    monto_convertido REAL NOT NULL,
                    fecha_tasa TEXT NOT NULL,
                    origen TEXT NOT NULL DEFAULT 'API',
                    fecha_registro TEXT NOT NULL,
                    id_empleado INTEGER,
                    id_proyecto INTEGER,
                    id_usuario INTEGER,
                    FOREIGN KEY(id_empleado) REFERENCES empleado(idUnico) ON DELETE SET NULL,
                    FOREIGN KEY(id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE SET NULL,
                    FOREIGN KEY(id_usuario) REFERENCES usuario(idUsuario) ON DELETE SET NULL
                )
            """)

            conn.commit()  # Guarda definitivamente los cambios en el archivo SQLite
        except sqlite3.Error as e:  # Si falla la creación de alguna tabla
            log.critical("Fallo al inicializar tablas SQLite: %s", e)  # Registra falla crítica
            raise RuntimeError("No fue posible preparar la base de datos del sistema.") from e
        finally:  # Se ejecuta siempre, haya habido error o no
            if conn:  # Verifica que la conexión se haya llegado a abrir
                conn.close()  # Cierra la conexión para liberar el archivo .db