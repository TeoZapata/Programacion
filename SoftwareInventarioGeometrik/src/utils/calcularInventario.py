import threading
from DataBase.storeDB import storeBD

class calcularInventario(threading.Thread):
    """Clase para calcular el inventario total."""

    def __init__(self):
        super().__init__()

    def run(self):
        """Método que se ejecuta al iniciar el hilo."""
        self.resultado = self.calcular_inventario()
        self.resultado_rojo = self.contar_productos_cantidad_cero()
        self.resultado_naranja = self.contar_productos_bajo_minimo()
        self.resultado_verde = self.contar_productos_entre_min_max()

    def calcular_inventario(self):
        """Calcula el inventario total y lo retorna."""
        db = storeBD()
        try:
            db.iniciar_bd()
            materiales = db.obtener_inventario()
            total_inventario = sum(material[7] for material in materiales if len(material) > 7 and isinstance(material[7], (int, float)))
            return f"${total_inventario:,.2f}"
        except Exception as e:
            print(f"Error al calcular el inventario: {e}")
            return 0

    def contar_productos_entre_min_max(self):
        """Cuenta los productos cuya cantidad está entre la cantidad mínima y máxima."""
        db = storeBD()
        try:
            db.iniciar_bd()
            materiales = db.obtener_inventario()
            productos_en_rango = sum(
                1 for material in materiales
                if material[8] <= int(material[4]) <= material[9]
            )

            return productos_en_rango
        except Exception as e:
            print(f"Error al contar productos entre min y max: {e}")
            return 0

    def contar_productos_bajo_minimo(self):
        """Cuenta los productos cuya cantidad está por debajo de la cantidad mínima, excluyendo los que tienen cantidad 0."""
        db = storeBD()
        try:
            db.iniciar_bd()
            materiales = db.obtener_inventario()
            productos_bajo_minimo = sum(1 for material in materiales if len(material) > 8 and isinstance(material[4], (int, float)) and isinstance(material[8], (int, float)) and material[4] < material[8] and material[4] > 0)
            return productos_bajo_minimo
        except Exception as e:
            print(f"Error al contar productos bajo mínimo: {e}")
            return 0

    def contar_productos_cantidad_cero(self):
        """Cuenta los productos cuya cantidad es igual a 0."""
        db = storeBD()
        try:
            db.iniciar_bd()
            materiales = db.obtener_inventario()
            productos_cantidad_cero = sum(1 for material in materiales if len(material) > 7 and isinstance(material[4], (int, float)) and material[4] == 0)
            return productos_cantidad_cero
        except Exception as e:
            print(f"Error al contar productos con cantidad 0: {e}")
            return 0

def iniciar_calculo_inventario(self):
    """Inicia el cálculo del inventario en un hilo separado."""

    # Crear una instancia de la clase calcularInventario

    hilo_calculo = calcularInventario()
    hilo_calculo.start()
    hilo_calculo.join()  # Espera a que el hilo termine antes de continuar
    self.precio_total_edit.setText(str( hilo_calculo.resultado))
    self.estado_rojo_edit.setText(str(hilo_calculo.resultado_rojo)) 
    self.estado_naranja_edit.setText(str(hilo_calculo.resultado_naranja))
    self.estado_verde_edit.setText(str(hilo_calculo.resultado_verde))


