import sqlite3  # Importa sqlite3 para manejo de excepciones SQL
from config.database import Database  # Importa la clase Singleton Database
from models.reporte_clima import ReporteClima  # Importa el modelo de dominio ReporteClima


class ReporteClimaDAO:  # Define el DAO encargado de la persistencia de reportes climáticos
    """
    Data Access Object para la persistencia de reportes meteorológicos en SQLite.
    """
    def __init__(self):  # Constructor del DAO
        self.db = Database()  # Obtiene la referencia al administrador de base de datos

    def insertar(self, reporte: ReporteClima) -> int | None:  # Guarda un reporte climático en SQLite
        sql = """
            INSERT INTO reporte_clima (
                ciudad, pais, temperatura, velocidad_viento, fecha_consulta, id_proyecto, id_usuario
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """  # Consulta SQL parametrizada para prevenir Inyección SQL
        conn = self.db.get_connection()  # Abre conexión
        try:  # Protege la inserción
            cursor = conn.cursor()  # Crea cursor
            cursor.execute(  # Ejecuta el INSERT pasando los atributos del objeto como tupla
                sql,
                (
                    reporte.ciudad,
                    reporte.pais,
                    reporte.temperatura,
                    reporte.velocidad_viento,
                    reporte.fecha_consulta,
                    reporte.id_proyecto,
                    reporte.id_usuario
                )
            )
            conn.commit()  # Guarda permanentemente el registro en SQLite
            return cursor.lastrowid  # Retorna el ID generado para el nuevo reporte
        except sqlite3.Error as e:  # Captura errores (por ejemplo, si el id_proyecto no existe)
            print(f"Error al guardar reporte de clima en BD: {e}")
            return None  # Retorna None indicando que no se pudo guardar
        finally:
            conn.close()  # Cierra la conexión

    def listar_todos(self) -> list[ReporteClima]:  # Recupera todo el historial de reportes climáticos
        sql = "SELECT * FROM reporte_clima ORDER BY id_reporte DESC"  # Ordena del más reciente al más antiguo
        conn = self.db.get_connection()  # Abre conexión
        reportes: list[ReporteClima] = []  # Lista donde se guardarán los objetos reconstruidos
        try:
            cursor = conn.cursor()  # Crea cursor
            cursor.execute(sql)  # Ejecuta la consulta
            for fila in cursor.fetchall():  # Itera sobre cada fila obtenida
                reportes.append(  # Crea un objeto ReporteClima por cada fila y lo añade a la lista
                    ReporteClima(
                        id_reporte=fila["id_reporte"],
                        ciudad=fila["ciudad"],
                        pais=fila["pais"],
                        temperatura=fila["temperatura"],
                        velocidad_viento=fila["velocidad_viento"],
                        fecha_consulta=fila["fecha_consulta"],
                        id_proyecto=fila["id_proyecto"],
                        id_usuario=fila["id_usuario"]
                    )
                )
        except sqlite3.Error as e:
            print(f"Error al listar reportes de clima: {e}")
        finally:
            conn.close()  # Cierra conexión
        return reportes  # Retorna la lista de reportes

    def obtener_por_proyecto(self, id_proyecto: int) -> list[ReporteClima]:  # Filtra reportes por proyecto
        sql = "SELECT * FROM reporte_clima WHERE id_proyecto = ? ORDER BY id_reporte DESC"  # Consulta parametrizada
        conn = self.db.get_connection()  # Abre conexión
        reportes: list[ReporteClima] = []  # Lista de resultados
        try:
            cursor = conn.cursor()  # Crea cursor
            cursor.execute(sql, (id_proyecto,))  # Ejecuta pasando el ID del proyecto como tupla
            for fila in cursor.fetchall():  # Recorre las filas coincidentes
                reportes.append(  # Reconstruye cada objeto ReporteClima
                    ReporteClima(
                        id_reporte=fila["id_reporte"],
                        ciudad=fila["ciudad"],
                        pais=fila["pais"],
                        temperatura=fila["temperatura"],
                        velocidad_viento=fila["velocidad_viento"],
                        fecha_consulta=fila["fecha_consulta"],
                        id_proyecto=fila["id_proyecto"],
                        id_usuario=fila["id_usuario"]
                    )
                )
        except sqlite3.Error as e:
            print(f"Error al consultar reportes por proyecto: {e}")
        finally:
            conn.close()  # Cierra conexión
        return reportes  # Retorna los reportes del proyecto