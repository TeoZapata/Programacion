import sqlite3
from datetime import datetime


class storeBD:
    def __init__ (self, db_name="inventario.db"):
        self.db_name=db_name
        self.iniciar_bd()
    
    def iniciar_bd(self):
        try :
            conexion = sqlite3.connect(self.db_name)
            cur = conexion.cursor()
            cur.execute('''CREATE TABLE IF NOT EXISTS inventario (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT,
                        seccion TEXT,
                        barcode VARCHAR(20) UNIQUE NOT NULL,
                        cantidad INTEGER,
                        unidad TEXT,
                        precio INTEGER,
                        precioTotal INTEGER,
                        cantidad_minima INTEGER,
                        cantidad_maxima INTEGER,
                        proveedor TEXT,
                        fecha_compra DATE
                        )''')
            cur.execute('''CREATE TABLE IF NOT EXISTS proyectos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        nombre TEXT,
                        cliente TEXT UNIQUE,
                        ubicacion INTEGER,
                        kwp INTEGER,
                        fechaCreacion DATE
                        )''')
            cur.execute('''CREATE TABLE IF NOT EXISTS materialProyecto (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        proyecto TEXT,
                        cliente TEXT,
                        responsable TEXT,
                        material TEXT,
                        cantidad INTEGER,
                        unidad TEXT,
                        precio INTEGER,
                        precioTotal INTEGER,
                        proveedor TEXT,
                        fecha DATE
                        )''')
            cur.execute(
                '''CREATE TABLE IF NOT EXISTS clientes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT,
                    email TEXT,
                    telefono TEXT,
                    direccion TEXT,
                    ciudad TEXT,
                    tipo TEXT
                )'''
            )
            cur.execute('''CREATE TABLE IF NOT EXISTS historial (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        proyecto TEXT,
                        referencia TEXT,
                        cliente TEXT,
                        responsable TEXT,
                        material TEXT,
                        cantidad INTEGER,
                        unidad TEXT,
                        precio INTEGER,
                        precioTotal INTEGER,
                        proveedor TEXT,
                        fecha DATE
                        )''')            
            
            conexion.commit()

        except sqlite3.Error as e:
            print(f"Error al iniciar la base de datos: {str(e)}")
        finally:
            conexion.close()
    def obtener_inventario(self):
        """Retorna la lista del inventario de la base de datos"""
        try:
            conexion = sqlite3.connect(self.db_name)
            cur = conexion.cursor()
            cur.execute("SELECT * FROM inventario")
            inventario = cur.fetchall()
            return inventario
        except sqlite3.Error as e:
            print(f"Error al obtener el inventario: {str(e)}")
            return []
        finally:
            conexion.close()

    def ejecutar_consulta(self, query, params=None):
        """
        Ejecuta una consulta SQL en la base de datos.
        
        Args:
            query (str): Consulta SQL a ejecutar
            params (tuple, optional): Parámetros para la consulta preparada
            
        Returns:
            list: Resultados de la consulta si es un SELECT
            int: Número de filas afectadas si es INSERT, UPDATE o DELETE
            
        Raises:
            Exception: Si ocurre un error en la consulta
        """
        try:
            conexion = sqlite3.connect(self.db_name)

            cursor = conexion.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            # Si es un SELECT, devolver resultados
            if query.strip().upper().startswith("SELECT"):
                results = cursor.fetchall()
                cursor.close()
                return results
            else:
                # Si es INSERT, UPDATE, DELETE
                conexion.commit()
                affected_rows = cursor.rowcount
                cursor.close()
                return affected_rows
                
        except Exception as e:
            # En caso de error, hacer rollback
            conexion.rollback()
            raise Exception(f"Error al ejecutar consulta: {str(e)}")
    def agregar_material(self, nombre:str, barcode:int, cantidad:int, unidad:str, precio:int, proveedor:str):
        """"Agrega Material a la base de datos del inventario"""
        formatted_precio = int(precio) #format the numbers with . for the thousend separatos, .0f removes the decimals
        precioTotal = "{:,.0f}".format(int(cantidad) * int(precio))
        try:
            conexion = sqlite3.connect(self.db_name)
            cur = conexion.cursor()
            cur.execute('''
                        INSERT INTO inventario (nombre, barcode, cantidad, unidad , precio ,precioTotal, proveedor, fecha_compra)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (nombre, barcode, cantidad, unidad ,formatted_precio, precioTotal ,proveedor, datetime.now().strftime("%Y-%m-%d")))
            
            conexion.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al agregar material: {str(e)}")
            return False
        finally:
            conexion.close()
    def buscar_material_por_nombre(self, nombre):
        """Busca materiales por nombre (usando LIKE)."""
        try:
            conexion = sqlite3.connect(self.db_name)
            cur = conexion.cursor()
            cur.execute("SELECT * FROM inventario WHERE nombre LIKE ?", (f"%{nombre}%",))
            resultados = cur.fetchall()
            return resultados
        except sqlite3.Error as e:
            print(f"Error al buscar material por nombre: {e}")
            return []
        finally:
            conexion.close()
            
    def eliminar_material(self, id_producto:int):
        try:
            conexion = sqlite3.connect(self.db_name)
            cur = conexion.cursor()
            cur.execute("DELETE FROM inventario WHERE id = ? ",(id_producto,))
            conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al eliminar material: {str(e)}")
        finally:
            conexion.close()
    def actualizar_material(self, nombre_material, nuevo_cantidad, nuevo_unidad ,nuevo_precio, proveedor, barcode):
        try:
            conexion = sqlite3.connect(self.db_name)
            cur = conexion.cursor()
            formatted_precio = int(nuevo_precio) #format the numbers with . for the thousend separatos, .0f removes the decimals
            precioTotal = "{:,.0f}".format(int(nuevo_cantidad) * int(nuevo_precio))
            cur.execute("UPDATE inventario SET nombre=?, cantidad=? , unidad=?, precio=? , precioTotal=?, proveedor=? ,fecha_compra=? WHERE barcode=? ",
                        (nombre_material, nuevo_cantidad, nuevo_unidad, formatted_precio , precioTotal, proveedor ,datetime.now().strftime("%Y-%m-%d"), barcode))
            conexion.commit()
        except sqlite3.Error as e:
            print(f"Error al actualizar material: {str(e)}")
        finally:
            conexion.close()
    def obtener_material_por_CD(self, barcode):
        try:
            conexion = sqlite3.connect(self.db_name)
            cur= conexion.cursor()
            cur.execute("SELECT * FROM inventario WHERE barcode=?", (barcode,))
            material = cur.fetchone()
            return material
        except sqlite3.Error as e:
            print(f"Error al obtener material por ID: {str(e)}")
            return None
        finally:
            conexion.close()
    
    
    