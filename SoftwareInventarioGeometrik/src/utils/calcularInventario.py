import threading
from DataBase.storeDB import storeBD

class calcularInventario(threading.Thread):
    """Clase para calcular el inventario total."""

    def __init__(self):
        super().__init__()

    def run(self):
        """Método que se ejecuta al iniciar el hilo."""
        self.resultado = self.calcular_inventario()

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

def iniciar_calculo_inventario(self):
    """Inicia el cálculo del inventario en un hilo separado."""

    # Crear una instancia de la clase calcularInventario

    hilo_calculo = calcularInventario()
    hilo_calculo.start()
    hilo_calculo.join()  # Espera a que el hilo termine antes de continuar
    self.precio_total_edit.setText(str( hilo_calculo.resultado))


