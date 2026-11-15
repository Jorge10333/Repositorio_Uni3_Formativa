import logging  # Registra errores técnicos en logs/ecotech.log
import sqlite3
from config.database import Database
from models.pago_internacional import PagoInternacional

log = logging.getLogger(__name__)


class PagoInternacionalDAO:  # Persistencia de pagos internacionales en SQLite
    @staticmethod
    def _mapear(fila: sqlite3.Row) -> PagoInternacional:
        return PagoInternacional(
            id_pago=fila["id_pago"],
            pais_proyecto=fila["pais_proyecto"],
            moneda_origen=fila["moneda_origen"],
            moneda_destino=fila["moneda_destino"],
            monto_base=fila["monto_base"],
            tasa_cambio=fila["tasa_cambio"],
            monto_convertido=fila["monto_convertido"],
            fecha_tasa=fila["fecha_tasa"],
            origen=fila["origen"],
            fecha_registro=fila["fecha_registro"],
            id_empleado=fila["id_empleado"],
            id_proyecto=fila["id_proyecto"],
            id_usuario=fila["id_usuario"],
        )

    @staticmethod
    def insertar(pago: PagoInternacional) -> int | None:
        sql = """
            INSERT INTO pago_internacional (
                pais_proyecto, moneda_origen, moneda_destino, monto_base,
                tasa_cambio, monto_convertido, fecha_tasa, origen, fecha_registro,
                id_empleado, id_proyecto, id_usuario
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = Database().get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    pago.pais_proyecto,
                    pago.moneda_origen,
                    pago.moneda_destino,
                    pago.monto_base,
                    pago.tasa_cambio,
                    pago.monto_convertido,
                    pago.fecha_tasa,
                    pago.origen,
                    pago.fecha_registro,
                    pago.id_empleado,
                    pago.id_proyecto,
                    pago.id_usuario,
                ),
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            log.error("Error al guardar pago internacional en BD: %s", e)
            return None
        finally:
            conn.close()

    @classmethod
    def listar_todos(cls) -> list[PagoInternacional]:
        conn = Database().get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM pago_internacional ORDER BY id_pago DESC")
            return [cls._mapear(f) for f in cursor.fetchall()]
        except sqlite3.Error as e:
            log.error("Error al listar pagos internacionales: %s", e)
            return []
        finally:
            conn.close()