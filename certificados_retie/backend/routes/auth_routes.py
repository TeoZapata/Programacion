"""
==============================================================
backend/routes/auth_routes.py
Rutas de autenticación: login, logout, gestión de usuarios
==============================================================
"""

from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, jsonify
)
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash
from datetime import datetime

from backend.database import db
from backend.models.user import User
from backend.utils.validators import admin_required, validar_email

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


# ── LOGIN ──────────────────────────────────────────────────

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Página de inicio de sesión."""
    if current_user.is_authenticated:
        return redirect(url_for("dashboard.index"))

    if request.method == "POST":
        usuario_input = request.form.get("usuario", "").strip()
        password = request.form.get("password", "")
        recordar = request.form.get("recordar", False)

        if not usuario_input or not password:
            flash("Por favor completa todos los campos.", "warning")
            return render_template("login.html")

        # Buscar por usuario o correo
        user = User.query.filter(
            (User.usuario == usuario_input) | (User.correo == usuario_input)
        ).first()

        if not user or not user.check_password(password):
            flash("Usuario o contraseña incorrectos.", "danger")
            return render_template("login.html")

        if not user.activo:
            flash("Tu cuenta está desactivada. Contacta al administrador.", "warning")
            return render_template("login.html")

        login_user(user, remember=bool(recordar))
        user.ultimo_login = datetime.utcnow()
        db.session.commit()

        next_page = request.args.get("next")
        return redirect(next_page or url_for("dashboard.index"))

    return render_template("login.html")


# ── LOGOUT ─────────────────────────────────────────────────

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("auth.login"))


# ── GESTIÓN DE USUARIOS (solo ADMIN) ──────────────────────

@auth_bp.route("/usuarios")
@login_required
@admin_required
def usuarios():
    """Lista todos los usuarios."""
    users = User.query.order_by(User.fecha_creacion.desc()).all()
    return render_template("usuarios.html", usuarios=users)


@auth_bp.route("/usuarios/nuevo", methods=["GET", "POST"])
@login_required
@admin_required
def nuevo_usuario():
    """Crea un nuevo usuario del sistema."""
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        correo = request.form.get("correo", "").strip().lower()
        usuario = request.form.get("usuario", "").strip().lower()
        password = request.form.get("password", "")
        rol = request.form.get("rol", "USUARIO")

        # Validaciones
        errores = []
        if not nombre:
            errores.append("El nombre es requerido.")
        if not correo or not validar_email(correo):
            errores.append("Correo electrónico inválido.")
        if not usuario or len(usuario) < 3:
            errores.append("El nombre de usuario debe tener al menos 3 caracteres.")
        if not password or len(password) < 6:
            errores.append("La contraseña debe tener al menos 6 caracteres.")
        if rol not in ["ADMIN", "USUARIO"]:
            errores.append("Rol inválido.")

        if User.query.filter_by(correo=correo).first():
            errores.append("El correo ya está registrado.")
        if User.query.filter_by(usuario=usuario).first():
            errores.append("El nombre de usuario ya existe.")

        if errores:
            for e in errores:
                flash(e, "danger")
            return render_template("nuevo_usuario.html")

        nuevo = User(
            nombre=nombre, correo=correo, usuario=usuario,
            password_hash=generate_password_hash(password),
            rol=rol, activo=True
        )
        db.session.add(nuevo)
        db.session.commit()
        flash(f"Usuario '{usuario}' creado exitosamente.", "success")
        return redirect(url_for("auth.usuarios"))

    return render_template("nuevo_usuario.html")


@auth_bp.route("/usuarios/<int:user_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_usuario(user_id):
    """Activa o desactiva un usuario."""
    user = User.query.get_or_404(user_id)
    if user.id == current_user.id:
        flash("No puedes desactivar tu propia cuenta.", "warning")
    else:
        user.activo = not user.activo
        db.session.commit()
        estado = "activado" if user.activo else "desactivado"
        flash(f"Usuario {user.usuario} {estado}.", "info")
    return redirect(url_for("auth.usuarios"))


@auth_bp.route("/usuarios/<int:user_id>/reset-password", methods=["POST"])
@login_required
@admin_required
def reset_password(user_id):
    """Reinicia la contraseña de un usuario."""
    user = User.query.get_or_404(user_id)
    nueva_pass = request.form.get("nueva_password", "")
    if len(nueva_pass) < 6:
        flash("La contraseña debe tener al menos 6 caracteres.", "danger")
    else:
        user.set_password(nueva_pass)
        db.session.commit()
        flash(f"Contraseña de {user.usuario} actualizada.", "success")
    return redirect(url_for("auth.usuarios"))


# ── PERFIL ─────────────────────────────────────────────────

@auth_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def perfil():
    """Página de perfil del usuario actual."""
    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        password_actual = request.form.get("password_actual", "")
        password_nuevo = request.form.get("password_nuevo", "")

        if nombre:
            current_user.nombre = nombre

        if password_actual and password_nuevo:
            if not current_user.check_password(password_actual):
                flash("La contraseña actual es incorrecta.", "danger")
                return render_template("perfil.html")
            if len(password_nuevo) < 6:
                flash("La nueva contraseña debe tener al menos 6 caracteres.", "danger")
                return render_template("perfil.html")
            current_user.set_password(password_nuevo)
            flash("Contraseña actualizada correctamente.", "success")

        db.session.commit()
        flash("Perfil actualizado.", "success")
        return redirect(url_for("auth.perfil"))

    return render_template("perfil.html")
