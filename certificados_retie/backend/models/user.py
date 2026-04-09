"""
==============================================================
backend/models/user.py
Modelo de Usuario con autenticación y roles ADMIN/USUARIO
==============================================================
"""

from backend.database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime


class User(UserMixin, db.Model):
    """Modelo de usuario del sistema."""

    __tablename__ = "usuarios"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre = db.Column(db.String(120), nullable=False)
    correo = db.Column(db.String(180), unique=True, nullable=False, index=True)
    usuario = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default="USUARIO")
    activo = db.Column(db.Boolean, default=True, nullable=False)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime, nullable=True)

    # Relación: un usuario puede registrar muchos certificados
    certificados = db.relationship(
        "Certificado", backref="registrado_por", lazy="dynamic"
    )

    # ── Métodos de contraseña ──────────────────────────────

    def set_password(self, password: str):
        """Hashea y guarda la contraseña."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Verifica la contraseña contra el hash almacenado."""
        return check_password_hash(self.password_hash, password)

    # ── Roles ──────────────────────────────────────────────

    @property
    def is_admin(self) -> bool:
        return self.rol == "ADMIN"

    # ── Flask-Login requerido ──────────────────────────────

    def get_id(self) -> str:
        return str(self.id)

    @property
    def is_active(self) -> bool:
        return self.activo

    # ── Serialización ─────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "correo": self.correo,
            "usuario": self.usuario,
            "rol": self.rol,
            "activo": self.activo,
            "fecha_creacion": self.fecha_creacion.strftime("%Y-%m-%d %H:%M") if self.fecha_creacion else None,
            "ultimo_login": self.ultimo_login.strftime("%Y-%m-%d %H:%M") if self.ultimo_login else "Nunca",
        }

    def __repr__(self):
        return f"<User {self.usuario} ({self.rol})>"
