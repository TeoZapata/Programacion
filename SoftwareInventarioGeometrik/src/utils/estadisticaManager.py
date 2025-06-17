import threading
from DataBase.storeDB import *
import pandas as pd

class EstadisticaManager(threading.Thread):
    """Clase para obtener datos estadísticos de la base de datos."""

    def __init__(self):
        super().__init__()
        self.db = storeBD()
    

    def run(self):
        self.inventario_stats = self.obtener_estadisticas_inventario()
        self.proveedores_stats = self.obtener_estadisticas_proveedores()
        self.herramientas_stats = self.obtener_estadisticas_herramientas()
        self.empleados_stats = self.obtener_estadisticas_empleados()
        self.proyectos_stats = self.obtener_estadisticas_proyectos()
        self.registro_stats = self.obtener_estadisticas_registro()
        self.clientes_stats = self.obtener_estadisticas_clientes()
        self.historial_stats = self.obtener_estadisticas_historial()
        self.informacion_stats = self.obtener_estadisticas_informacion()

    def obtener_estadisticas_inventario(self):
        """Retorna estadísticas útiles del inventario."""
        db = self.db
        try:
            materiales = db.ejecutar_consulta("SELECT * FROM inventario", ())
            df = pd.DataFrame(materiales)
            total_productos = len(materiales)
            total_valor = sum(m[7] for m in materiales if len(m) > 7 and isinstance(m[7], (int, float)))
            productos_bajo_min = sum(1 for m in materiales if len(m) > 8 and isinstance(m[4], int) and isinstance(m[8], int) and m[4] < m[8])
            productos_sin_stock = sum(1 for m in materiales if len(m) > 4 and isinstance(m[4], int) and m[4] == 0)
            productos_sobre_max = sum(1 for m in materiales if len(m) > 9 and isinstance(m[4], int) and isinstance(m[9], int) and m[4] > m[9])
            return {
                'Datos':{"total_productos": total_productos,
                "productos_bajo_min": productos_bajo_min,
                "productos_sin_stock": productos_sin_stock,
                "productos_sobre_max": productos_sobre_max,},
                "DataFrame" : df
            }
        except Exception as e:
            print(f"Error en inventario: {e}")
            return {}

    def obtener_estadisticas_proveedores(self):
        """Retorna cantidad de proveedores y ciudades distintas."""
        db = self.db
        try:
            proveedores = db.ejecutar_consulta("SELECT * FROM proveedores", ())
            df = pd.DataFrame(proveedores)
            total_proveedores = len(proveedores)
            ciudades = set(p[6] for p in proveedores if len(p) > 6)
            return {
                'Datos':{"total_proveedores": total_proveedores},
                "DataFrame" : df
            }
        except Exception as e:
            print(f"Error en proveedores: {e}")
            return {}

    def obtener_estadisticas_herramientas(self):
        """Retorna cantidad de herramientas asignadas y estados distintos."""
        db = self.db
        try:
            herramientas = db.ejecutar_consulta("SELECT * FROM gestionHerramientas", ())
            df = pd.DataFrame(herramientas)
            total_asignaciones = len(herramientas)
            estados = set(h[9] for h in herramientas if len(h) > 9)
            return {
                'Datos':{"total_asignaciones": total_asignaciones},
                "DataFrame" : df
            }
        except Exception as e:
            print(f"Error en herramientas: {e}")
            return {}

    def obtener_estadisticas_empleados(self):
        """Retorna cantidad de empleados y cargos distintos."""
        db = self.db
        try:
            empleados = db.ejecutar_consulta("SELECT * FROM empleados", ())
            df = pd.DataFrame(empleados)
            total_empleados = len(empleados)
            cargos = set(e[3] for e in empleados if len(e) > 3)
            return {
                'Datos':{"total_empleados": total_empleados,
                "cargos_distintos": len(cargos)},
                "DataFrame" : df
            }
        except Exception as e:
            print(f"Error en empleados: {e}")
            return {}

    def obtener_estadisticas_proyectos(self):
        """Retorna cantidad de proyectos y suma de kwp."""
        db = self.db
        try:
            proyectos = db.ejecutar_consulta("SELECT * FROM proyectos", ())
            df = pd.DataFrame(proyectos)
            total_proyectos = len(proyectos)
            total_kwp = sum(p[4] for p in proyectos if len(p) > 4 and isinstance(p[4], (int, float)))
            return {
                'Datos':{"total_proyectos": total_proyectos,
                "total_kwp": total_kwp},
                "DataFrame" : df
            }
        except Exception as e:
            print(f"Error en proyectos: {e}")
            return {}

    def obtener_estadisticas_registro(self):
        """Retorna cantidad de registros y suma de precios totales."""
        db = self.db
        try:
            registros = db.ejecutar_consulta("SELECT * FROM registro", ())
            df = pd.DataFrame(registros)
            total_registros = len(registros)
            total_precio = sum(r[10] for r in registros if len(r) > 10 and isinstance(r[10], (int, float)))
            return {
                'Datos':{"total_registros": total_registros,
                "total_precio": total_precio},
                "dataFrame" : df
            }
        except Exception as e:
            print(f"Error en registro: {e}")
            return {}

    def obtener_estadisticas_clientes(self):
        """Retorna cantidad de clientes y ciudades distintas."""
        db = self.db
        try:
            clientes = db.ejecutar_consulta("SELECT * FROM clientes", ())
            df = pd.DataFrame(clientes)
            total_clientes = len(clientes)
            ciudades = set(c[5] for c in clientes if len(c) > 5)
            return {
                'Datos':{"total_clientes": total_clientes},
                "DataFrame" : df 
            }
        except Exception as e:
            print(f"Error en clientes: {e}")
            return {}

    def obtener_estadisticas_historial(self):
        """Retorna cantidad de movimientos y suma de precios totales."""
        db = self.db
        try:
            historial = db.ejecutar_consulta("SELECT * FROM historial", ())
            df = pd.DataFrame(historial)
            total_movimientos = len(historial)
            total_precio = sum(h[8] for h in historial if len(h) > 8 and isinstance(h[8], (int, float)))
            return {
                'Datos':{"total_movimientos": total_movimientos,
                "total_precio": total_precio},
                "DataFrame" : df
            }
        except Exception as e:
            print(f"Error en historial: {e}")
            return {}

    def obtener_estadisticas_informacion(self):
        """Retorna los contadores generales de la tabla informacion."""
        db = self.db
        try:
            info = db.ejecutar_consulta("SELECT * FROM informacion", ())
            df = pd.DataFrame(info)
            if info and len(info[0]) >= 6:
                return {
                    'Datos':{"cantSalidas": info[0][1],
                    "cantEntradas": info[0][2],
                    "cantDevoluciones": info[0][3],
                    "cantCodigosBarras": info[0][4],
                    "cantReporteHerramientas": info[0][5]},
                    "DataFrame" : df
                }
            return {}
        except Exception as e:
            print(f"Error en informacion: {e}")
            return {}


