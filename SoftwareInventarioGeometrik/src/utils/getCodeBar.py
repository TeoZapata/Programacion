from random import randint
from barcode import Code128
from barcode.writer import ImageWriter
from random import choice
from string import ascii_uppercase
from DataBase.storeDB import *



def obtener_nombre_empleado():
    db =conex()
    datos = db.ejecutar_consulta("SELECT nombre FROM empleados")
    nombres = [dato[0] for dato in datos]
    return nombres
def obtener_nombres_proveedores():
    db = conex()
    datos = db.ejecutar_consulta("SELECT nombre FROM proveedores")
    nombres = [dato[0] for dato in datos]
    return nombres
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
    "m^3", # Metro cúbico
    "kg",    # Kilogramo
    "pqte", # Paquete
    "gal",   # Galón
    "ml",    # Mililitro
    ]

    return unidades

def getCodeBar(self=None, categoria='EQUIPO', subcategoria='TORNILLERÍA', camp:bool=True):
    """Genera un código de barras en formato letra-números-letra (ejemplo: X785163A)."""


    lista_categoria, lista_subcategoria = obtener_categorias()
    
    

    if not hasattr(getCodeBar, "counter"):
        db = conex()

        getCodeBar.counter = db.ejecutar_consulta(
            "SELECT MAX(id) FROM inventario"
        )[0][0] or 0


    code = (
        '71'
        + lista_categoria[categoria]
        + lista_subcategoria[subcategoria]
        + f"{getCodeBar.counter:03d}"
    )
    
    getCodeBar.counter += 1
    
    if camp:
        self.line_edits['Código de Barras'].setText(code)

    



    return code

def conex():
    """Establece una conexión a la base de datos."""
    db = storeBD()
    db.iniciar_bd()

    return db