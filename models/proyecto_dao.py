from sqlite3 import Cursor
from config.database import Database
from .proyecto import Proyecto

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
        except Exception as e:
            print(f"Error al crear proyecto: {e}")
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
        except Exception as e:
            print(f"Error al obtener proyectos: {e}")
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
        except Exception as e:
            print(f"Error al obtener proyecto por ID: {e}")
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
        except Exception as e:
            print(f"Error al actualizar proyecto: {e}")
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
        except Exception as e:
            print(f"Error al eliminar proyecto: {e}")
            return False
        finally:
            conn.close()