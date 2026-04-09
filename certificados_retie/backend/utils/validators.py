"""
==============================================================
backend/utils/validators.py
Validadores y utilidades de seguridad del sistema RETIE
==============================================================
"""

import re
import os
from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user


# ── Validación de archivos ──────────────────────────────────

ALLOWED_EXTENSIONS = {"pdf"}
MAX_FILE_SIZE_MB = 50


def validar_extension_pdf(filename: str) -> bool:
    """Verifica que el archivo sea un PDF por extensión."""
    if not filename:
        return False
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def validar_archivo_pdf_magic(file_bytes: bytes) -> bool:
    """Verifica firma magic bytes del PDF (%PDF-)."""
    return file_bytes[:5] == b"%PDF-"


# ── Validación de formularios ───────────────────────────────

def validar_numero_certificado(numero: str) -> bool:
    """Valida formato básico de número de certificado."""
    if not numero or len(numero.strip()) < 3:
        return False
    return bool(re.match(r'^[A-Za-z0-9\-/\.\s]{3,100}$', numero.strip()))


def validar_email(email: str) -> bool:
    """Valida formato de correo electrónico."""
    pattern = r'^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validar_fecha_formato(fecha_str: str) -> bool:
    """Verifica que la fecha tenga formato válido."""
    if not fecha_str:
        return True  # Fecha vacía es válida (opcional)
    from datetime import datetime
    for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y"]:
        try:
            datetime.strptime(fecha_str, fmt)
            return True
        except ValueError:
            continue
    return False


# ── Decoradores de control de acceso ───────────────────────

def admin_required(f):
    """Decorador: solo permite acceso a usuarios con rol ADMIN."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return redirect(url_for("auth.login"))
        if not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function


def login_and_role_required(roles: list):
    """Decorador configurable por roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for("auth.login"))
            if current_user.rol not in roles:
                abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator


# ── Sanitización ────────────────────────────────────────────

def sanitizar_nombre_archivo(filename: str) -> str:
    """Elimina caracteres peligrosos de nombres de archivo."""
    from werkzeug.utils import secure_filename
    return secure_filename(filename)


def sanitizar_texto(texto: str, max_len: int = 500) -> str:
    """Limpia texto de entrada eliminando caracteres peligrosos."""
    if not texto:
        return ""
    texto = texto.strip()[:max_len]
    # Eliminar caracteres de control
    texto = re.sub(r'[\x00-\x1f\x7f-\x9f]', '', texto)
    return texto
