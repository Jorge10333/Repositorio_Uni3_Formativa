from sqlite3 import Cursor
from config.database import Database
from .departamento import Departamento

class DepartamentoDAO:
    """
    DAO encargada de la persistencia de Departamento en BD.
    """
    @staticmethod
    def crear(departamento: Departamento) -> bool:
        # Inserta un nuevo departamento y asigna el ID generado
        conn = Database().get_connection()
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO departamento (nombre, id_gerente) VALUES (?, ?)",
                (departamento.nombre, departamento.id_gerente)
            )
            conn.commit()
            departamento.id_departamento = cursor.lastrowid
            return True
        except Exception as e:
            print(f"Error al crear departamento en BD: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def obtener_todos() -> list[Departamento]:
        # Consulta y mapea todos los departamentos
        conn = Database().get_connection()
        departamentos = []
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute("SELECT id_departamento, nombre, id_gerente FROM departamento")
            filas = cursor.fetchall()
            for fila in filas:
                departamentos.append(Departamento(fila['nombre'], fila['id_gerente'], fila['id_departamento']))
        except Exception as e:
            print(f"Error al obtener departamentos: {e}")
        finally:
            conn.close()
        return departamentos

    @staticmethod
    def obtener_por_id(id_departamento: int) -> Departamento | None:
        # Busca un departamento por su ID único
        conn = Database().get_connection()
        departamento = None
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute("SELECT id_departamento, nombre, id_gerente FROM departamento WHERE id_departamento = ?", (id_departamento,))
            fila = cursor.fetchone()
            if fila:
                departamento = Departamento(fila['nombre'], fila['id_gerente'], fila['id_departamento'])
        except Exception as e:
            print(f"Error al obtener el departamento: {e}")
        finally:
            conn.close()
        return departamento

    @staticmethod
    def actualizar(departamento: Departamento) -> bool:
        # Modifica los datos de un departamento existente
        if departamento.id_departamento is None:
            return False
        conn = Database().get_connection()
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute(
                "UPDATE departamento SET nombre = ?, id_gerente = ? WHERE id_departamento = ?",
                (departamento.nombre, departamento.id_gerente, departamento.id_departamento)
            )
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al actualizar departamento: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def eliminar(id_departamento: int) -> bool:
        # Elimina una fila por clave primaria
        conn = Database().get_connection()
        try:
            cursor: Cursor = conn.cursor()
            cursor.execute("DELETE FROM departamento WHERE id_departamento = ?", (id_departamento,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error al eliminar departamento: {e}")
            return False
        finally:
            conn.close()