import logging
import sqlite3
from sqlite3 import Cursor
from config.database import Database
from .empleado import Empleado
from .departamento_dao import DepartamentoDAO

log = logging.getLogger(__name__)

class EmpleadoDAO:
    """
    DAO encargada de la persistencia de Empleado en BD.
    """
    @staticmethod
    def crear(empleado: Empleado) -> bool:
        # Inserta registro de empleado guardando la FK del departamento asociado
        conn = Database().get_connection()
        try:
            cursor: Cursor = conn.cursor()
            id_depto = empleado.departamento.id_departamento if empleado.departamento else None
            cursor.execute(
                """
                INSERT INTO empleado (nombre, direccion, telefono, email, fechaInicio, salario, id_departamento)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    empleado.nombre,
                    empleado.direccion,
                    empleado.telefono,
                    empleado.email,
                    empleado.fecha_inicio,
                    empleado.salario,
                    id_depto
                )
            )
            conn.commit()
            empleado.id_unico = cursor.lastrowid
            return True
        except sqlite3.IntegrityError as e:
            log.warning("Empleado no creado (restricción de BD): %s", e)
            return False
        except sqlite3.Error as e:
            log.error("Error al crear empleado en BD: %s", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def obtener_todos() -> list[Empleado]:
        # Obtiene la lista de empleados y reconstruye el objeto Departamento mediante su DAO
        conn = Database().get_connection()
        empleados = []
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute("SELECT * FROM empleado")
            filas = cursor.fetchall()
            for fila in filas:
                depto = None
                if fila['id_departamento'] is not None:
                    depto = DepartamentoDAO.obtener_por_id(fila['id_departamento'])
                empleados.append(
                    Empleado(
                        nombre=fila['nombre'],
                        direccion=fila['direccion'],
                        telefono=fila['telefono'],
                        email=fila['email'],
                        fecha_inicio=fila['fechaInicio'],
                        salario=fila['salario'],
                        departamento=depto,
                        id_unico=fila['idUnico']
                    )
                )
        except sqlite3.Error as e:
            log.error("Error al obtener empleados: %s", e)
        finally:
            conn.close()
        return empleados

    @staticmethod
    def obtener_por_id(id_unico: int) -> Empleado | None:
        # Recupera un empleado por su ID único incluyendo el objeto Departamento
        conn = Database().get_connection()
        empleado = None
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute("SELECT * FROM empleado WHERE idUnico = ?", (id_unico,))
            fila = cursor.fetchone()
            if fila:
                depto = None
                if fila['id_departamento'] is not None:
                    depto = DepartamentoDAO.obtener_por_id(fila['id_departamento'])
                empleado = Empleado(
                    nombre=fila['nombre'],
                    direccion=fila['direccion'],
                    telefono=fila['telefono'],
                    email=fila['email'],
                    fecha_inicio=fila['fechaInicio'],
                    salario=fila['salario'],
                    departamento=depto,
                    id_unico=fila['idUnico']
                )
        except sqlite3.Error as e:
            log.error("Error al obtener empleado por ID: %s", e)
        finally:
            conn.close()
        return empleado

    @staticmethod
    def actualizar(empleado: Empleado) -> bool:
        # Modifica todos los atributos del empleado en la BD
        if empleado.id_unico is None:
            return False
        conn = Database().get_connection()
        try:
            cursor: Cursor = conn.cursor()
            id_depto = empleado.departamento.id_departamento if empleado.departamento else None
            cursor.execute(
                """
                UPDATE empleado
                SET nombre = ?, direccion = ?, telefono = ?, email = ?, fechaInicio = ?, salario = ?, id_departamento = ?
                WHERE idUnico = ?
                """,
                (
                    empleado.nombre,
                    empleado.direccion,
                    empleado.telefono,
                    empleado.email,
                    empleado.fecha_inicio,
                    empleado.salario,
                    id_depto,
                    empleado.id_unico
                )
            )
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            log.warning("Empleado no actualizado (restricción de BD): %s", e)
            return False
        except sqlite3.Error as e:
            log.error("Error al actualizar empleado: %s", e)
            return False
        finally:
            conn.close()

    @staticmethod
    def eliminar(id_unico: int) -> bool:
        # Borra al empleado por ID (el CASCADE elimina usuarios o registros asociados)
        conn = Database().get_connection()
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute("DELETE FROM empleado WHERE idUnico = ?", (id_unico,))
            conn.commit()
            return cursor.rowcount > 0
        except sqlite3.IntegrityError as e:
            log.warning("Empleado no eliminado (restricción de BD): %s", e)
            return False
        except sqlite3.Error as e:
            log.error("Error al eliminar empleado: %s", e)
            return False
        finally:
            conn.close()