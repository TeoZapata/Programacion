"""
==============================================================
backend/database.py
Configuración de SQLAlchemy y seeding inicial de datos
==============================================================
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash
import logging

logger = logging.getLogger(__name__)

db = SQLAlchemy()


def init_db(app):
    """
    Inicializa la base de datos:
    - Crea las tablas si no existen
    - Crea el usuario ADMIN inicial si no hay usuarios
    """
    from backend.models.user import User

    with app.app_context():
        # Crear usuario admin por defecto si la BD está vacía
        if User.query.count() == 0:
            admin = User(
                nombre="Administrador",
                correo="admin@retie.local",
                usuario="admin",
                password_hash=generate_password_hash("admin123"),
                rol="ADMIN",
                activo=True
            )
            db.session.add(admin)
            db.session.commit()
            logger.info("Usuario ADMIN inicial creado: admin / admin123")
            print("\n[RETIE] Usuario inicial creado:")
            print("  Usuario: admin")
            print("  Password: admin123")
            print("  ⚠️  Cambia la contraseña después del primer login\n")
