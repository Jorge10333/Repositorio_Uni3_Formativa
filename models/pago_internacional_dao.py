import sqlite3  # Importa sqlite3 para capturar excepciones de base de datos
from config.database import Database  # Importa la conexión Singleton
from models.pago_internacional import PagoInternacional  # Importa el modelo PagoInternacional


class PagoInternacionalDAO:  # Define el DAO para persistir pagos internacionales en SQLite
    """
    Data Access Object para guardar y consultar pagos internacionales en SQLite.
    """
    def __init__(self):  # Constructor del DAO
        self.db = Database()  # Obtiene la instancia de Database

    def insertar(self, pago: PagoInternacional) -> int | None:  # Inserta un cálculo de pago en la BD
        sql = """
            INSERT INTO pago_internacional (
                pais_proyecto, moneda_origen, moneda_destino, monto_base,
                tasa_cambio, monto_convertido, fecha_tasa, fecha_registro,
                id_empleado, id_proyecto, id_usuario
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """  # Consulta SQL parametrizada (?) para neutralizar Inyección SQL
        conn = self.db.get_connection()  # Abre conexión con SQLite
        try:  # Protege la inserción contra errores de claves foráneas o disco
            cursor = conn.cursor()  # Crea el cursor SQL
            cursor.execute(  # Ejecuta la inserción pasando los datos como tupla separada
                sql,
                (
                    pago.pais_proyecto,
                    pago.moneda_origen,
                    pago.moneda_destino,
                    pago.monto_base,
                    pago.tasa_cambio,
                    pago.monto_convertido,
                    pago.fecha_tasa,
                    pago.fecha_registro,
                    pago.id_empleado,
                    pago.id_proyecto,
                    pago.id_usuario
                )
            )
            conn.commit()  # Guarda permanentemente el registro en SQLite
            return cursor.lastrowid  # Retorna el ID autoincremental generado
        except sqlite3.Error as e:  # Captura errores de SQLite (ej. id_empleado o id_proyecto inexistente)
            print(f"Error al guardar pago internacional en BD: {e}")
            return None  # Retorna None indicando que no se guardó
        finally:
            conn.close()  # Cierra la conexión

    def listar_todos(self) -> list[PagoInternacional]:  # Lista todos los pagos internacionales registrados
        sql = "SELECT * FROM pago_internacional ORDER BY id_pago DESC"  # Ordena del más reciente al más antiguo
        conn = self.db.get_connection()  # Abre conexión
        pagos: list[PagoInternacional] = []  # Lista vacía para almacenar los objetos reconstruidos
        try:
            cursor = conn.cursor()  # Crea cursor
            cursor.execute(sql)  # Ejecuta consulta
            for fila in cursor.fetchall():  # Recorre cada fila devuelta por SQLite
                pagos.append(  # Reconstruye cada objeto PagoInternacional y lo agrega a la lista
                    PagoInternacional(
                        id_pago=fila["id_pago"],
                        pais_proyecto=fila["pais_proyecto"],
                        moneda_origen=fila["moneda_origen"],
                        moneda_destino=fila["moneda_destino"],
                        monto_base=fila["monto_base"],
                        tasa_cambio=fila["tasa_cambio"],
                        monto_convertido=fila["monto_convertido"],
                        fecha_tasa=fila["fecha_tasa"],
                        fecha_registro=fila["fecha_registro"],
                        id_empleado=fila["id_empleado"],
                        id_proyecto=fila["id_proyecto"],
                        id_usuario=fila["id_usuario"]
                    )
                )
        except sqlite3.Error as e:
            print(f"Error al listar pagos internacionales: {e}")
        finally:
            conn.close()  # Cierra conexión
        return pagos  # Retorna la lista completa de pagos