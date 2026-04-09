"""
==============================================================
backend/config.py
Configuraciones por entorno del sistema RETIE
==============================================================
"""

import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig:
    """Configuración base compartida."""
    SECRET_KEY = os.getenv("SECRET_KEY", "retie-secret-key-2024-cambiar-en-produccion")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Directorio de uploads
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
    PDF_FOLDER = os.path.join(BASE_DIR, "uploads", "pdf")
    IMAGES_FOLDER = os.path.join(BASE_DIR, "uploads", "images")
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50 MB max upload

    # Extensiones permitidas
    ALLOWED_EXTENSIONS = {"pdf"}

    # Sesión
    PERMANENT_SESSION_LIFETIME = timedelta(hours=8)
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"

    # Alertas de vencimiento (días)
    ALERT_DAYS_CRITICAL = 30
    ALERT_DAYS_WARNING = 60
    ALERT_DAYS_NOTICE = 90

    # Paginación
    ITEMS_PER_PAGE = 20

    # Tesseract (ajustar ruta según sistema operativo)
    TESSERACT_CMD = os.getenv("TESSERACT_CMD", "/usr/bin/tesseract")

    @staticmethod
    def ensure_upload_dirs():
        """Crea los directorios de uploads si no existen."""
        for path_attr in ["PDF_FOLDER", "IMAGES_FOLDER"]:
            path = os.path.join(BASE_DIR, "uploads",
                                "pdf" if "PDF" in path_attr else "images")
            os.makedirs(path, exist_ok=True)


class DevelopmentConfig(BaseConfig):
    """Configuración para desarrollo (SQLite local)."""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.join(BASE_DIR, 'retie_dev.db')}"
    )
    SQLALCHEMY_ECHO = False  # True para ver queries SQL


class ProductionConfig(BaseConfig):
    """Configuración para producción (PostgreSQL)."""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "postgresql://retie_user:retie_pass@localhost:5432/retie_db"
    )
    SESSION_COOKIE_SECURE = True

    # Seguridad adicional en producción
    WTF_CSRF_ENABLED = True


class TestingConfig(BaseConfig):
    """Configuración para pruebas automatizadas."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_map = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
    "default": DevelopmentConfig,
}
