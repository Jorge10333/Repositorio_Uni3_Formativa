from sqlite3 import Cursor
from config.database import Database
from .proyecto import Proyecto
import logging
import sqlite3

log = logging.getLogger(__name__)

class ProyectoDAO:
    """
    DAO encargada de la persistencia de Proyecto en BD.
    """
    @staticmethod
    def crear(proyecto: Proyecto) -> bool:
        # Guarda un nuevo proyecto
        conn = Database().get_connection()
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO proyecto (nombre, descripcion, fechaInicio) VALUES (?, ?, ?)",
                (proyecto.nombre, proyecto.descripcion, proyecto.fecha_inicio)
            )
            conn.commit()
            proyecto.id_proyecto = cursor.lastrowid
            return True
        except sqlite3.IntegrityError as e:
            log.warning("Proyecto no creado (restricción de BD): %s", e)
            return False
        except sqlite3.Error as e:
            log.error("Error al crear proyecto en BD: %s", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def obtener_todos() -> list[Proyecto]:
        # Lista todos los proyectos disponibles
        conn = Database().get_connection()
        proyectos = []
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute("SELECT * FROM proyecto")
            filas = cursor.fetchall()
            for fila in filas:
                proyectos.append(
                    Proyecto(
                        nombre=fila['nombre'],
                        descripcion=fila['descripcion'],
                        fecha_inicio=fila['fechaInicio'],
                        id_proyecto=fila['id_proyecto']
                    )
                )
        except sqlite3.Error as e:
            log.error("Error al obtener proyectos: %s", e)
        finally:
            conn.close()
        return proyectos

    @staticmethod
    def obtener_por_id(id_proyecto: int) -> Proyecto | None:
        # Obtiene un proyecto según su clave primaria
        conn = Database().get_connection()
        proyecto = None
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute("SELECT * FROM proyecto WHERE id_proyecto = ?", (id_proyecto,))
            fila = cursor.fetchone()
            if fila:
                proyecto = Proyecto(
                    nombre=fila['nombre'],
                    descripcion=fila['descripcion'],
                    fecha_inicio=fila['fechaInicio'],
                    id_proyecto=fila['id_proyecto']
                )
        except sqlite3.Error as e:
            log.error("Error al obtener proyecto: %s", e)
        finally:
            conn.close()
        return proyecto

    @staticmethod
    def actualizar(proyecto: Proyecto) -> bool:
        # Actualiza la información del proyecto
        if proyecto.id_proyecto is None:
            return False
        conn = Database().get_connection()
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "UPDATE proyecto SET nombre = ?, descripcion = ?, fechaInicio = ? WHERE id_proyecto = ?",
                (proyecto.nombre, proyecto.descripcion, proyecto.fecha_inicio, proyecto.id_proyecto)
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            log.warning("Proyecto no actualizado (restricción de BD): %s", e)
            return False
        except sqlite3.Error as e:
            log.error("Error al actualizar proyecto: %s", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def eliminar(id_proyecto: int) -> bool:
        # Borra el proyecto por ID
        conn = Database().get_connection()
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute("DELETE FROM proyecto WHERE id_proyecto = ?", (id_proyecto,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            log.warning("Proyecto no eliminado (restricción de BD): %s", e)
            return False
        except sqlite3.Error as e:
            log.error("Error al eliminar proyecto: %s", e)
            return False
        finally:
            conn.close()