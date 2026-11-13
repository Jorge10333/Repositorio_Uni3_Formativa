import sqlite3
from sqlite3 import Cursor
from config.database import Database
from .registro_tiempo import RegistroTiempo  # Importación corregida

class RegistroTiempoDAO:
    """
    Data Access Object para la entidad RegistroTiempo.
    """
    @staticmethod
    def crear(registro: RegistroTiempo) -> bool:
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO registro_tiempo (fecha, cantidadHoraTrabajada, descripcionTareaRealizada, id_empleado, id_proyecto)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    registro.fecha,
                    registro.cantidad_hora_trabajada,
                    registro.descripcion_tarea_realizada,
                    registro.id_empleado,
                    registro.id_proyecto
                )
            )
            conn.commit()
            registro.id_registro = cursor.lastrowid
            return True
        except sqlite3.Error as e:
            print(f"Error al registrar tiempo en BD: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def obtener_por_empleado(id_empleado: int) -> list[RegistroTiempo]:
        conn = None
        registros = []
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute("SELECT * FROM registro_tiempo WHERE id_empleado = ?", (id_empleado,))
            filas = cursor.fetchall()
            for fila in filas:
                registros.append(
                    RegistroTiempo(
                        fecha=fila['fecha'],
                        cantidad_hora_trabajada=fila['cantidadHoraTrabajada'],
                        descripcion_tarea_realizada=fila['descripcionTareaRealizada'],
                        id_empleado=fila['id_empleado'],
                        id_proyecto=fila['id_proyecto'],
                        id_registro=fila['id_registro']
                    )
                )
        except sqlite3.Error as e:
            print(f"Error al obtener registros de tiempo por empleado: {e}")
        finally:
            if conn:
                conn.close()
        return registros

    @staticmethod
    def eliminar(id_registro: int) -> bool:
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute("DELETE FROM registro_tiempo WHERE id_registro = ?", (id_registro,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al eliminar registro de tiempo: {e}")
            return False
        finally:
            if conn:
                conn.close()