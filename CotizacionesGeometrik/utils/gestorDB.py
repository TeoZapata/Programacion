

import sqlite3
import json
import pandas as pd

class DatabaseManager:
    def __init__(self, db_name="solar_quotes.db"):
        self.db_name = db_name
        self.init_database()
    
    def init_database(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Tabla de clientes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                cedula TEXT NOT NULL,
                telefono TEXT,
                email TEXT,
                direccion TEXT,
                ciudad TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabla de cotizaciones
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cotizaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                consumo_promedio REAL,
                tipo_facturacion TEXT,
                consumos TEXT,
                ciudad TEXT,
                irradiacion REAL,
                potencia_requerida REAL,
                iva_porcentaje REAL,
                utilidad_porcentaje REAL,
                imprevistos_porcentaje REAL,
                num_trabajadores INTEGER,
                dias_trabajo INTEGER,
                precio_trabajador REAL,
                costo_total REAL,
                fecha_cotizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (cliente_id) REFERENCES clientes (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insertar_cliente(self, datos_cliente):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO clientes (nombre, cedula, telefono, email, direccion, ciudad)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datos_cliente['nombre'],
            datos_cliente['cedula'],
            datos_cliente['telefono'],
            datos_cliente['email'],
            datos_cliente['direccion'],
            datos_cliente['ciudad']
        ))
        
        cliente_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cliente_id
    
    def insertar_cotizacion(self, cliente_id, datos_cotizacion):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO cotizaciones (
                cliente_id, consumo_promedio, tipo_facturacion, consumos,
                ciudad, irradiacion, potencia_requerida, iva_porcentaje,
                utilidad_porcentaje, imprevistos_porcentaje, num_trabajadores,
                dias_trabajo, precio_trabajador, costo_total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            cliente_id,
            datos_cotizacion['consumo_promedio'],
            datos_cotizacion['tipo_facturacion'],
            json.dumps(datos_cotizacion['consumos']),
            datos_cotizacion['ciudad'],
            datos_cotizacion['irradiacion'],
            datos_cotizacion['potencia_requerida'],
            datos_cotizacion['iva_porcentaje'],
            datos_cotizacion['utilidad_porcentaje'],
            datos_cotizacion['imprevistos_porcentaje'],
            datos_cotizacion['num_trabajadores'],
            datos_cotizacion['dias_trabajo'],
            datos_cotizacion['precio_trabajador'],
            datos_cotizacion['costo_total']
        ))
        
        cotizacion_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return cotizacion_id
    
    def obtener_cotizaciones(self):
        conn = sqlite3.connect(self.db_name)
        query = '''
            SELECT c.id, cl.nombre, cl.ciudad, c.potencia_requerida, 
                   c.costo_total, c.fecha_cotizacion
            FROM cotizaciones c
            JOIN clientes cl ON c.cliente_id = cl.id
            ORDER BY c.fecha_cotizacion DESC
        '''
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
