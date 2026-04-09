import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_DIR = BASE_DIR / "database"
DATABASE_DIR.mkdir(exist_ok=True)

DATABASE_URL = f"sqlite:///{DATABASE_DIR}/geoinventario.db"

APP_NAME = "GeoInventario"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Área de Ingeniería — Ing. Mateo Salazar Zapata"
APP_CREDITS = "Creado por el Área de Ingeniería\nIng. Mateo Salazar Zapata"

# Roles
ROLES = {
    "administrador": "Administrador",
    "tecnico": "Técnico",
    "inventario": "Inventario",
}

# Colores del tema
THEME = {
    "primary": "#1E3A5F",
    "secondary": "#2ECC71",
    "accent": "#F39C12",
    "danger": "#E74C3C",
    "bg": "#F5F6FA",
    "card": "#FFFFFF",
    "text": "#2C3E50",
    "text_light": "#7F8C8D",
    "border": "#DDE2E8",
    "sidebar": "#1E3A5F",
    "sidebar_hover": "#2980B9",
}

# Categorías de inventario
CATEGORIAS_INVENTARIO = [
    "Paneles Solares",
    "Inversores",
    "Baterías",
    "Estructuras",
    "Cableado",
    "Protecciones",
    "Herramientas",
    "Consumibles",
    "Otros",
]

# Estados de proyecto
ESTADOS_PROYECTO = [
    "Prospecto",
    "En diseño",
    "Aprobado",
    "En ejecución",
    "Completado",
    "Cancelado",
]
