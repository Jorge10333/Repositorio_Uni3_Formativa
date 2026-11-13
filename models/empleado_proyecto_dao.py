import sqlite3
from sqlite3 import Cursor
from config.database import Database
from .empleado_proyecto import EmpleadoProyecto  # Importación corregida

class EmpleadoProyectoDAO:
    """
    DAO para gestionar la asignación de empleados a proyectos (Relación N:M).
    """
    @staticmethod
    def asignar(asignacion: EmpleadoProyecto) -> bool:
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO empleado_proyecto (id_empleado, id_proyecto) VALUES (?, ?)",
                (asignacion.id_empleado, asignacion.id_proyecto)
            )
            conn.commit()
            asignacion.id_empleado_proyecto = cursor.lastrowid
            return True
        except sqlite3.Error as e:
            print(f"Error al asignar empleado a proyecto en BD: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def desasignar(id_empleado: int, id_proyecto: int) -> bool:
        conn = None
        try:
            conn = Database().get_connection()
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM empleado_proyecto WHERE id_empleado = ? AND id_proyecto = ?",
                (id_empleado, id_proyecto)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"Error al desasignar empleado del proyecto: {e}")
            return False
        finally:
            if conn:
                conn.close()