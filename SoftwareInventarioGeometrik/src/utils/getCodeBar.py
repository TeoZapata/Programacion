from random import randint
from barcode import Code128
from barcode.writer import ImageWriter
from random import choice
from string import ascii_uppercase


def obtener_categorias():
    categoria = {
        "MATERIAL": "00",
        "HERRAMIENTA": "01",
        "EQUIPO": "02",
        "MAQUINARIA": "03",
        "PAPELERÍA": "04",
        "MOBILIARIO": "05",
        "SST": "06",
        "EPP": "07",
        "DOTACIÓN": "08",
        "EQUIPAMIENTO": "09",
        'None':'xx'
    }
    subcategoria = {
        "ELÉCTRICO AC": "00",
        "ELÉCTRICO DC": "01",
        "ELÉCTRICO": "02",
        "ESTRUCTURA": "03",
        "PFV": "04",
        "TORNILLERÍA": "05",
        "HIDRÁULICO": "06",
        "QUÍMICOS": "07",
        "OBRA CIVIL": "08",
        "ELECTRÓNICA": "09",
        "TELEMETRÍA": "10",
        "FOTOGRAMETRÍA": "11",
        "MEDICIÓN": "12",
        "MANTENIMIENTO SFV": "13",
        "SOLDADURA": "14",
        "METALMECÁNICA": "15",
        "COLECTOR SOLAR": "16",
        "SST": "17",
        "SCI": "18",
        "TSA": "19",
        "TC": "20",
        "PARTÍCULAS": "21",
        "RODILLAS": "22",
        "MANOS": "23",
        "OCULAR": "24",
        "PRENDA": "25",
        "ELECTRODOMÉSTICO": "26",
        "INTERNET": "27",
        "ROTULACIÓN": "28",
        "ALMACENAMIENTO": "29",
        "VARIOS": "30",
        "SILLAS": "31",
        "MESAS": "32",
        "None": "xx"
    }
    return categoria, subcategoria
def obtener_unidades():
    unidades = [
    "ud",   # Unidad
    "m",     # Metro
    "kg",    # Kilogramo
    "pqte", # Paquete
    "gal",   # Galón
    "l",     # Litro
    ]

    return unidades

def getCodeBar(self=None, categoria='EQUIPO', subcategoria='TORNILLERÍA', camp:bool=True):
    """Genera un código de barras en formato letra-números-letra (ejemplo: X785163A)."""


    lista_categoria, lista_subcategoria = obtener_categorias()
    

    code = (
        '71'  # Primera letra
        +lista_categoria[categoria]  # Seis dígitos
        +lista_subcategoria[subcategoria] # Última letra
        +str(randint(0, 999)).zfill(3) )  # Números aleatorios
    
    
    if camp:
        self.line_edits['Código de Barras'].setText(code)

    



    return code
