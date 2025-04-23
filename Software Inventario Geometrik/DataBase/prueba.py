import mysql.connector
from mysql.connector import Error
from datetime import datetime
import pandas as pd
from tabulate import tabulate
import os

class AlmacenDB:
    def __init__(self, host="localhost", user="root", password="password", database="almacen_db"):
        """Inicializa la conexión a la base de datos"""
        try:
            self.connection = mysql.connector.connect(
                host=host,
                user=user,
                password=password,
                database=database
            )
            if self.connection.is_connected():
                self.cursor = self.connection.cursor(dictionary=True)
                print("Conexión exitosa a la base de datos")
        except Error as e:
            print(f"Error al conectar a MySQL: {e}")
    
    def close_connection(self):
        """Cierra la conexión a la base de datos"""
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.cursor.close()
            self.connection.close()
            print("Conexión a MySQL cerrada")
    
    # ===== OPERACIONES CRUD PARA CLIENTES =====
    
    def crear_cliente(self, nombre, apellido, empresa=None, telefono=None, email=None, direccion=None):
        """Crea un nuevo cliente en la base de datos"""
        try:
            query = """
            INSERT INTO Clientes (nombre, apellido, empresa, telefono, email, direccion)
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            values = (nombre, apellido, empresa, telefono, email, direccion)
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"Cliente {nombre} {apellido} creado con ID: {self.cursor.lastrowid}")
            return self.cursor.lastrowid
        except Error as e:
            print(f"Error al crear cliente: {e}")
            return None
    
    def leer_cliente(self, cliente_id=None):
        """Lee información de cliente(s). Si se proporciona ID, lee uno específico"""
        try:
            if cliente_id:
                query = "SELECT * FROM Clientes WHERE cliente_id = %s"
                self.cursor.execute(query, (cliente_id,))
                result = self.cursor.fetchone()
                if result:
                    return result
                else:
                    print(f"No se encontró cliente con ID {cliente_id}")
                    return None
            else:
                query = "SELECT * FROM Clientes ORDER BY nombre, apellido"
                self.cursor.execute(query)
                return self.cursor.fetchall()
        except Error as e:
            print(f"Error al leer cliente(s): {e}")
            return None
    
    def actualizar_cliente(self, cliente_id, nombre=None, apellido=None, empresa=None, 
                         telefono=None, email=None, direccion=None):
        """Actualiza información de un cliente existente"""
        try:
            # Primero verificamos que el cliente exista
            cliente = self.leer_cliente(cliente_id)
            if not cliente:
                return False
            
            # Construimos la consulta dinámicamente para actualizar solo los campos proporcionados
            update_fields = []
            values = []
            
            if nombre:
                update_fields.append("nombre = %s")
                values.append(nombre)
            if apellido:
                update_fields.append("apellido = %s")
                values.append(apellido)
            if empresa is not None:
                update_fields.append("empresa = %s")
                values.append(empresa)
            if telefono is not None:
                update_fields.append("telefono = %s")
                values.append(telefono)
            if email is not None:
                update_fields.append("email = %s")
                values.append(email)
            if direccion is not None:
                update_fields.append("direccion = %s")
                values.append(direccion)
            
            if not update_fields:
                print("No se proporcionaron campos para actualizar")
                return False
            
            query = f"UPDATE Clientes SET {', '.join(update_fields)} WHERE cliente_id = %s"
            values.append(cliente_id)
            
            self.cursor.execute(query, tuple(values))
            self.connection.commit()
            print(f"Cliente con ID {cliente_id} actualizado exitosamente")
            return True
        except Error as e:
            print(f"Error al actualizar cliente: {e}")
            return False
    
    def eliminar_cliente(self, cliente_id):
        """Elimina un cliente (desactivándolo, no borrándolo físicamente)"""
        try:
            # Verificamos si tiene proyectos asociados
            query = "SELECT COUNT(*) as count FROM Proyectos WHERE cliente_id = %s"
            self.cursor.execute(query, (cliente_id,))
            result = self.cursor.fetchone()
            
            if result['count'] > 0:
                print(f"No se puede eliminar cliente con ID {cliente_id} porque tiene proyectos asociados")
                return False
            
            # Si no tiene proyectos, lo marcamos como inactivo
            query = "UPDATE Clientes SET activo = FALSE WHERE cliente_id = %s"
            self.cursor.execute(query, (cliente_id,))
            self.connection.commit()
            print(f"Cliente con ID {cliente_id} marcado como inactivo")
            return True
        except Error as e:
            print(f"Error al eliminar cliente: {e}")
            return False
    
    # ===== OPERACIONES CRUD PARA PROYECTOS =====
    
    def crear_proyecto(self, cliente_id, nombre_proyecto, descripcion=None, 
                      fecha_inicio=None, fecha_fin_estimada=None, presupuesto=None):
        """Crea un nuevo proyecto para un cliente"""
        try:
            # Verificamos que el cliente exista
            cliente = self.leer_cliente(cliente_id)
            if not cliente:
                print(f"No existe cliente con ID {cliente_id}")
                return None
            
            query = """
            INSERT INTO Proyectos (cliente_id, nombre_proyecto, descripcion, fecha_inicio, 
                                 fecha_fin_estimada, presupuesto, estado)
            VALUES (%s, %s, %s, %s, %s, %s, 'Pendiente')
            """
            values = (cliente_id, nombre_proyecto, descripcion, fecha_inicio, 
                     fecha_fin_estimada, presupuesto)
            
            self.cursor.execute(query, values)
            self.connection.commit()
            print(f"Proyecto '{nombre_proyecto}' creado con ID: {self.cursor.lastrowid}")
            return self.cursor.lastrowid
        except Error as e:
            print(f"Error al crear proyecto: {e}")
            return None
    
    def leer_proyecto(self, proyecto_id=None):
        """Lee información de proyecto(s). Si se proporciona ID, lee uno específico"""
        try:
            if proyecto_id:
                query = """
                SELECT p.*, c.nombre, c.apellido 
                FROM Proyectos p
                JOIN Clientes c ON p.cliente_id = c.cliente_id
                WHERE p.proyecto_id = %s
                """
                self.cursor.execute(query, (proyecto_id,))
                result = self.cursor.fetchone()
                if result:
                    return result
                else:
                    print(f"No se encontró proyecto con ID {proyecto_id}")
                    return None
            else:
                query = """
                SELECT p.*, c.nombre, c.apellido 
                FROM Proyectos p
                JOIN Clientes c ON p.cliente_id = c.cliente_id
                ORDER BY p.fecha_inicio DESC
                """
                self.cursor.execute(query)
                return self.cursor.fetchall()
        except Error as e:
            print(f"Error al leer proyecto(s): {e}")
            return None
    
    def actualizar_proyecto(self, proyecto_id, nombre_proyecto=None, descripcion=None, 
                          fecha_inicio=None, fecha_fin_estimada=None, fecha_fin_real=None,
                          estado=None, presupuesto=None):
        """Actualiza información de un proyecto existente"""
        try:
            # Verificamos que el proyecto exista
            proyecto = self.leer_proyecto(proyecto_id)
            if not proyecto:
                return False
            
            # Construimos la consulta dinámicamente
            update_fields = []
            values = []
            
            if nombre_proyecto:
                update_fields.append("nombre_proyecto = %s")
                values.append(nombre_proyecto)
            if descripcion is not None:
                update_fields.append("descripcion = %s")
                values.append(descripcion)
            if fecha_inicio:
                update_fields.append("fecha_inicio = %s")
                values.append(fecha_inicio)
            if fecha_fin_estimada:
                update_fields.append("fecha_fin_estimada = %s")
                values.append(fecha_fin_estimada)
            if fecha_fin_real:
                update_fields.append("fecha_fin_real = %s")
                values.append(fecha_fin_real)
            if estado and estado in ['Pendiente', 'En Progreso', 'Finalizado', 'Cancelado']:
                update_fields.append("estado = %s")
                values.append(estado)
            if presupuesto is not None:
                update_fields.append("presupuesto = %s")
                values.append(presupuesto)
            
            if not update_fields:
                print("No se proporcionaron campos para actualizar")
                return False
            
            query = f"UPDATE Proyectos SET {', '.join(update_fields)} WHERE proyecto_id = %s"
            values.append(proyecto_id)
            
            self.cursor.execute(query, tuple(values))
            self.connection.commit()
            print(f"Proyecto con ID {proyecto_id} actualizado exitosamente")
            return True
        except Error as e:
            print(f"Error al actualizar proyecto: {e}")
            return False
    
    def eliminar_proyecto(self, proyecto_id):
        """Cambia el estado del proyecto a 'Cancelado'"""
        try:
            # Verificamos primero si tiene movimientos asociados
            query = "SELECT COUNT(*) as count FROM MovimientosAlmacen WHERE proyecto_id = %s"
            self.cursor.execute(query, (proyecto_id,))
            result = self.cursor.fetchone()
            
            if result['count'] > 0:
                print(f"No se puede eliminar proyecto con ID {proyecto_id} porque tiene movimientos asociados")
                print("Se marcará como 'Cancelado' en su lugar")
                return self.actualizar_proyecto(proyecto_id, estado='Cancelado')
            
            # Si no tiene movimientos, podemos eliminarlo físicamente
            query = "DELETE FROM Proyectos WHERE proyecto_id = %s"
            self.cursor.execute(query, (proyecto_id,))
            self.connection.commit()
            print(f"Proyecto con ID {proyecto_id} eliminado exitosamente")
            return True
        except Error as e:
            print(f"Error al eliminar proyecto: {e}")
            return False
    
    # ===== OPERACIONES CRUD PARA PRODUCTOS =====
    
    def crear_producto(self, codigo, nombre, categoria_id=None, descripcion=None, 
                     unidad_medida="unidad", precio_unitario=0, stock_inicial=0, stock_minimo=5):
        """Crea un nuevo producto en el inventario"""
        try:
            query = """
            INSERT INTO Productos (codigo, nombre, categoria_id, descripcion, unidad_medida, 
                                 precio_unitario, stock_actual, stock_minimo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (codigo, nombre, categoria_id, descripcion, unidad_medida, 
                     precio_unitario, stock_inicial, stock_minimo)
            
            self.cursor.execute(query, values)
            self.connection.commit()
            
            producto_id = self.cursor.lastrowid
            print(f"Producto '{nombre}' creado con ID: {producto_id}")
            
            # Si hay stock inicial, registramos un movimiento de entrada
            if stock_inicial > 0:
                # Primero creamos un movimiento de entrada
                query_mov = """
                INSERT INTO MovimientosAlmacen (tipo_movimiento_id, fecha_movimiento, referencia, observaciones)
                VALUES (1, NOW(), %s, %s)
                """
                values_mov = (f"Entrada inicial {codigo}", f"Stock inicial del producto {nombre}")
                self.cursor.execute(query_mov, values_mov)
                movimiento_id = self.cursor.lastrowid
                
                # Luego creamos el detalle del movimiento
                query_det = """
                INSERT INTO DetalleMovimientos (movimiento_id, producto_id, cantidad, precio_unitario)
                VALUES (%s, %s, %s, %s)
                """
                values_det = (movimiento_id, producto_id, stock_inicial, precio_unitario)
                self.cursor.execute(query_det, values_det)
                self.connection.commit()
                
                print(f"Registrada entrada inicial de {stock_inicial} unidades")
            
            return producto_id
        except Error as e:
            print(f"Error al crear producto: {e}")
            return None
    
    def leer_producto(self, producto_id=None, codigo=None):
        """Lee información de producto(s). Si se proporciona ID o código, lee uno específico"""
        try:
            if producto_id:
                query = """
                SELECT p.*, c.nombre as categoria_nombre 
                FROM Productos p
                LEFT JOIN Categorias c ON p.categoria_id = c.categoria_id
                WHERE p.producto_id = %s
                """
                self.cursor.execute(query, (producto_id,))
                result = self.cursor.fetchone()
                if result:
                    return result
                else:
                    print(f"No se encontró producto con ID {producto_id}")
                    return None
            elif codigo:
                query = """
                SELECT p.*, c.nombre as categoria_nombre 
                FROM Productos p
                LEFT JOIN Categorias c ON p.categoria_id = c.categoria_id
                WHERE p.codigo = %s
                """
                self.cursor.execute(query, (codigo,))
                result = self.cursor.fetchone()
                if result:
                    return result
                else:
                    print(f"No se encontró producto con código {codigo}")
                    return None
            else:
                query = """
                SELECT p.*, c.nombre as categoria_nombre 
                FROM Productos p
                LEFT JOIN Categorias c ON p.categoria_id = c.categoria_id
                WHERE p.activo = TRUE
                ORDER BY p.nombre
                """
                self.cursor.execute(query)
                return self.cursor.fetchall()
        except Error as e:
            print(f"Error al leer producto(s): {e}")
            return None
    
    def actualizar_producto(self, producto_id, codigo=None, nombre=None, categoria_id=None, 
                          descripcion=None, unidad_medida=None, precio_unitario=None, stock_minimo=None):
        """Actualiza información de un producto existente"""
        try:
            # Verificamos que el producto exista
            producto = self.leer_producto(producto_id=producto_id)
            if not producto:
                return False
            
            # Construimos la consulta dinámicamente
            update_fields = []
            values = []
            
            if codigo:
                update_fields.append("codigo = %s")
                values.append(codigo)
            if nombre:
                update_fields.append("nombre = %s")
                values.append(nombre)
            if categoria_id is not None:
                update_fields.append("categoria_id = %s")
                values.append(categoria_id)
            if descripcion is not None:
                update_fields.append("descripcion = %s")
                values.append(descripcion)
            if unidad_medida:
                update_fields.append("unidad_medida = %s")
                values.append(unidad_medida)
            if precio_unitario is not None:
                update_fields.append("precio_unitario = %s")
                values.append(precio_unitario)
            if stock_minimo is not None:
                update_fields.append("stock_minimo = %s")
                values.append(stock_minimo)
            
            if not update_fields:
                print("No se proporcionaron campos para actualizar")
                return False
            
            query = f"UPDATE Productos SET {', '.join(update_fields)} WHERE producto_id = %s"
            values.append(producto_id)
            
            self.cursor.execute(query, tuple(values))
            self.connection.commit()
            print(f"Producto con ID {producto_id} actualizado exitosamente")
            return True
        except Error as e:
            print(f"Error al actualizar producto: {e}")
            return False
    
    def eliminar_producto(self, producto_id):
        """Marca un producto como inactivo (no se elimina físicamente)"""
        try:
            query = "UPDATE Productos SET activo = FALSE WHERE producto_id = %s"
            self.cursor.execute(query, (producto_id,))
            self.connection.commit()
            print(f"Producto con ID {producto_id} marcado como inactivo")
            return True
        except Error as e:
            print(f"Error al eliminar producto: {e}")
            return False
    
    # ===== OPERACIONES PARA MOVIMIENTOS DE ALMACÉN =====
    
    def registrar_entrada_almacen(self, producto_id, cantidad, precio_unitario=None, referencia=None, observaciones=None):
        """Registra una entrada de productos al almacén"""
        try:
            # Verificamos que el producto exista
            producto = self.leer_producto(producto_id=producto_id)
            if not producto:
                return False
            
            # Si no se proporciona un precio, usamos el último registrado
            if precio_unitario is None:
                precio_unitario = producto['precio_unitario']
            
            # Creamos el movimiento
            query_mov = """
            INSERT INTO MovimientosAlmacen (tipo_movimiento_id, fecha_movimiento, referencia, observaciones)
            VALUES (1, NOW(), %s, %s)
            """
            values_mov = (referencia or f"Entrada {producto['codigo']}", 
                         observaciones or f"Entrada de producto {producto['nombre']}")
            
            self.cursor.execute(query_mov, values_mov)
            movimiento_id = self.cursor.lastrowid
            
            # Creamos el detalle del movimiento
            query_det = """
            INSERT INTO DetalleMovimientos (movimiento_id, producto_id, cantidad, precio_unitario)
            VALUES (%s, %s, %s, %s)
            """
            values_det = (movimiento_id, producto_id, cantidad, precio_unitario)
            self.cursor.execute(query_det, values_det)
            self.connection.commit()
            
            print(f"Registrada entrada de {cantidad} unidades de {producto['nombre']}")
            return movimiento_id
        except Error as e:
            print(f"Error al registrar entrada: {e}")
            return None
    
    def registrar_salida_almacen(self, proyecto_id, producto_id, cantidad, referencia=None, observaciones=None):
        """Registra una salida de productos del almacén hacia un proyecto"""
        try:
            # Verificamos que el producto y proyecto existan
            producto = self.leer_producto(producto_id=producto_id)
            proyecto = self.leer_proyecto(proyecto_id=proyecto_id)
            
            if not producto or not proyecto:
                return False
            
            # Verificamos que haya suficiente stock
            if producto['stock_actual'] < cantidad:
                print(f"Stock insuficiente. Disponible: {producto['stock_actual']}, Solicitado: {cantidad}")
                return False
            
            # Creamos el movimiento
            query_mov = """
            INSERT INTO MovimientosAlmacen (tipo_movimiento_id, proyecto_id, fecha_movimiento, referencia, observaciones)
            VALUES (2, %s, NOW(), %s, %s)
            """
            values_mov = (proyecto_id, 
                         referencia or f"Salida para proyecto {proyecto['nombre_proyecto']}", 
                         observaciones or f"Salida de {producto['nombre']} para proyecto {proyecto['nombre_proyecto']}")
            
            self.cursor.execute(query_mov, values_mov)
            movimiento_id = self.cursor.lastrowid
            
            # Creamos el detalle del movimiento
            query_det = """
            INSERT INTO DetalleMovimientos (movimiento_id, producto_id, cantidad, precio_unitario)
            VALUES (%s, %s, %s, %s)
            """
            values_det = (movimiento_id, producto_id, cantidad, producto['precio_unitario'])
            self.cursor.execute(query_det, values_det)
            self.connection.commit()
            
            print(f"Registrada salida de {cantidad} unidades de {producto['nombre']} para proyecto {proyecto['nombre_proyecto']}")
            return movimiento_id
        except Error as e:
            print(f"Error al registrar salida: {e}")
            return None
    
    def registrar_devolucion_almacen(self, proyecto_id, producto_id, cantidad, referencia=None, observaciones=None):
        """Registra una devolución de productos desde un proyecto al almacén"""
        try:
            # Verificamos que el producto y proyecto existan
            producto = self.leer_producto(producto_id=producto_id)
            proyecto = self.leer_proyecto(proyecto_id=proyecto_id)
            
            if not producto or not proyecto:
                return False
            
            # Verificamos que el proyecto tenga asignado este producto
            query = """
            SELECT cantidad_asignada, cantidad_devuelta 
            FROM ProyectoProductos 
            WHERE proyecto_id = %s AND producto_id = %s
            """
            self.cursor.execute(query, (proyecto_id, producto_id))
            result = self.cursor.fetchone()
            
            if not result:
                print(f"El producto {producto['nombre']} no ha sido asignado al proyecto {proyecto['nombre_proyecto']}")
                return False
            
            disponible_devolucion = result['cantidad_asignada'] - result['cantidad_devuelta']
            if disponible_devolucion < cantidad:
                print(f"No se puede devolver más producto del asignado. Disponible: {disponible_devolucion}, Solicitado: {cantidad}")
                return False
            
            # Creamos el movimiento
            query_mov = """
            INSERT INTO MovimientosAlmacen (tipo_movimiento_id, proyecto_id, fecha_movimiento, referencia, observaciones)
            VALUES (3, %s, NOW(), %s, %s)
            """
            values_mov = (proyecto_id, 
                         referencia or f"Devolución desde proyecto {proyecto['nombre_proyecto']}", 
                         observaciones or f"Devolución de {producto['nombre']} desde proyecto {proyecto['nombre_proyecto']}")
            
            self.cursor.execute(query_mov, values_mov)
            movimiento_id = self.cursor.lastrowid
            
            # Creamos el detalle del movimiento
            query_det = """
            INSERT INTO DetalleMovimientos (movimiento_id, producto_id, cantidad, precio_unitario)
            VALUES (%s, %s, %s, %s)
            """
            values_det = (movimiento_id, producto_id, cantidad, producto['precio_unitario'])
            self.cursor.execute(query_det, values_det)
            self.connection.commit()
            
            print(f"Registrada devolución de {cantidad} unidades de {producto['nombre']} desde proyecto {proyecto['nombre_proyecto']}")
            return movimiento_id
        except Error as e:
            print(f"Error al registrar devolución: {e}")
            return None
    
    # ===== CONSULTAS Y VISTAS =====
    
    def vista_inventario_actual(self):
        """Muestra el inventario actual"""
        try:
            query = "SELECT * FROM VistaInventarioActual"
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            
            if len(result) == 0:
                print("No hay productos en el inventario")
                return []
            
            # Creamos un DataFrame para mostrar los resultados de forma ordenada
            df = pd.DataFrame(result)
            
            # Mostrar tabla formateada
            print("\n===== INVENTARIO ACTUAL =====")
            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
            
            return result
        except Error as e:
            print(f"Error al consultar inventario: {e}")
            return None
    
    def vista_productos_por_proyecto(self, proyecto_id=None):
        """Muestra los productos asignados a proyectos"""
        try:
            if proyecto_id:
                query = "SELECT * FROM VistaProductosPorProyecto WHERE proyecto_id = %s"
                self.cursor.execute(query, (proyecto_id,))
            else:
                query = "SELECT * FROM VistaProductosPorProyecto"
                self.cursor.execute(query)
            
            result = self.cursor.fetchall()
            
            if len(result) == 0:
                print("No hay productos asignados a proyectos")
                return []
            
            # Creamos un DataFrame para mostrar los resultados de forma ordenada
            df = pd.DataFrame(result)
            
            # Mostrar tabla formateada
            if proyecto_id:
                proyecto_nombre = result[0]['nombre_proyecto']
                print(f"\n===== PRODUCTOS DEL PROYECTO: {proyecto_nombre} =====")
            else:
                print("\n===== PRODUCTOS POR PROYECTO =====")
            
            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
            
            return result
        except Error as e:
            print(f"Error al consultar productos por proyecto: {e}")
            return None
    
    def vista_historial_movimientos(self, proyecto_id=None, producto_id=None, tipo_movimiento=None):
        """Muestra el historial de movimientos con filtros opcionales"""
        try:
            conditions = []
            values = []
            
            if proyecto_id:
                conditions.append("proyecto_id = %s")
                values.append(proyecto_id)
            
            if producto_id:
                conditions.append("producto_id = %s")
                values.append(producto_id)
            
            if tipo_movimiento:
                conditions.append("tipo_movimiento = %s")
                values.append(tipo_movimiento)
            
            query = "SELECT * FROM VistaHistorialMovimientos"
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            
            query += " ORDER BY fecha_movimiento DESC"
            
            self.cursor.execute(query, tuple(values))
            result = self.cursor.fetchall()
            
            if len(result) == 0:
                print("No hay movimientos que coincidan con los filtros")
                return []
            
            # Creamos un DataFrame para mostrar los resultados de forma ordenada
            df = pd.DataFrame(result)
            
            # Mostrar tabla formateada
            print("\n===== HISTORIAL DE MOVIMIENTOS =====")
            if conditions:
                print("Filtros aplicados: " + ", ".join(conditions))
            
            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
            
            return result
        except Error as e:
            print(f"Error al consultar historial de movimientos: {e}")
            return None
    
    def reporte_productos_bajo_stock(self):
        """Muestra productos con stock por debajo del mínimo"""
        try:
            query = """
            SELECT p.codigo, p.nombre, c.nombre as categoria, p.stock_actual, p.stock_minimo, 
                  (p.stock_minimo - p.stock_actual) as faltante, p.unidad_medida
            FROM Productos p
            LEFT JOIN Categorias c ON p.categoria_id = c.categoria_id
            WHERE p.activo = TRUE AND p.stock_actual < p.stock_minimo
            ORDER BY (p.stock_minimo - p.stock_actual) DESC
            """
            
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            
            if len(result) == 0:
                print("No hay productos con stock bajo")
                return []
            
            # Creamos un DataFrame para mostrar los resultados de forma ordenada
            df = pd.DataFrame(result)
            
            # Mostrar tabla formateada
            print("\n===== PRODUCTOS CON STOCK BAJO =====")
            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
            
            return result
        except Error as e:
            print(f"Error al generar reporte de stock bajo: {e}")
            return None
    
    def reporte_proyectos_activos(self):
        """Muestra los proyectos activos con su información básica"""
        try:
            query = """
            SELECT p.proyecto_id, p.nombre_proyecto, c.nombre, c.apellido,
                  p.fecha_inicio, p.fecha_fin_estimada, p.estado, p.presupuesto,
                  (SELECT SUM(dm.subtotal) FROM MovimientosAlmacen ma
                   JOIN DetalleMovimientos dm ON ma.movimiento_id = dm.movimiento_id
                   WHERE ma.proyecto_id = p.proyecto_id AND ma.tipo_movimiento_id = 2) as costo_actual
            FROM Proyectos p
            JOIN Clientes c ON p.cliente_id = c.cliente_id
            WHERE p.estado IN ('Pendiente', 'En Progreso')
            ORDER BY p.fecha_inicio DESC
            """
            
            self.cursor.execute(query)
            result = self.cursor.fetchall()
            
            if len(result) == 0:
                print("No hay proyectos activos")
                return []
            
            # Creamos un DataFrame para mostrar los resultados de forma ordenada
            df = pd.DataFrame(result)
            
            # Mostrar tabla formateada
            print("\n===== PROYECTOS ACTIVOS =====")
            print(tabulate(df, headers='keys', tablefmt='psql', showindex=False))
            
            return result
        except Error as e:
            print(f"Error al generar reporte de proyectos activos: {e}")
            return None


# Ejemplo de uso
def ejemplo_uso():
    db = AlmacenDB()
    
    # Crear algunos registros de ejemplo
    print("\n1. Creando cliente")
    cliente_id = db.crear_cliente("Juan", "Pérez", empresa="Geometrik", telefono="123456789", email="teo@hotmail.com")