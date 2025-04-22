
from datetime import datetime

def fecha_actual():
    """Devuelve la fecha actual en formato 'dd/mm/yyyy'."""
    return datetime.now().strftime("%d/%m/%Y")