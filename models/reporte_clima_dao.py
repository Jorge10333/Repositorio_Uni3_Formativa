# --- models/reporte_clima_dao.py ---
import logging 
import sqlite3
from config.database import Database
from models.reporte_clima import ReporteClima

log = logging.getLogger(__name__)


class ReporteClimaDAO:  # Persistencia de reportes meteorológicos en SQLite
    @staticmethod
    def _mapear(fila: sqlite3.Row) -> ReporteClima:
        return ReporteClima(
            id_reporte=fila["id_reporte"],
            ciudad=fila["ciudad"],
            pais=fila["pais"],
            temperatura=fila["temperatura"],
            humedad=fila["humedad"],
            codigo_clima=fila["codigo_clima"],
            descripcion_clima=fila["descripcion_clima"],
            velocidad_viento=fila["velocidad_viento"],
            origen=fila["origen"],
            fecha_consulta=fila["fecha_consulta"],
            id_proyecto=fila["id_proyecto"],
            id_usuario=fila["id_usuario"],
        )

    @staticmethod
    def insertar(reporte: ReporteClima) -> int | None:
        sql = """
            INSERT INTO reporte_clima (
                ciudad, pais, temperatura, humedad, codigo_clima, descripcion_clima,
                velocidad_viento, origen, fecha_consulta, id_proyecto, id_usuario
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        conn = Database().get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                sql,
                (
                    reporte.ciudad,
                    reporte.pais,
                    reporte.temperatura,
                    reporte.humedad,
                    reporte.codigo_clima,
                    reporte.descripcion_clima,
                    reporte.velocidad_viento,
                    reporte.origen,
                    reporte.fecha_consulta,
                    reporte.id_proyecto,
                    reporte.id_usuario,
                ),
            )
            conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            log.error("Error al guardar reporte de clima en BD: %s", e)
            return None
        finally:
            conn.close()

    @classmethod
    def listar_todos(cls) -> list[ReporteClima]:
        conn = Database().get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reporte_clima ORDER BY id_reporte DESC")
            return [cls._mapear(f) for f in cursor.fetchall()]
        except sqlite3.Error as e:
            log.error("Error al listar reportes de clima: %s", e)
            return []
        finally:
            conn.close()

    @classmethod
    def obtener_por_proyecto(cls, id_proyecto: int) -> list[ReporteClima]:
        conn = Database().get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM reporte_clima WHERE id_proyecto = ? ORDER BY id_reporte DESC",
                (id_proyecto,),
            )
            return [cls._mapear(f) for f in cursor.fetchall()]
        except sqlite3.Error as e:
            log.error("Error al consultar reportes del proyecto %s: %s", id_proyecto, e)
            return []
        finally:
            conn.close()