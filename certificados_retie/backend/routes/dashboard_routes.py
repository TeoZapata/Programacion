"""
==============================================================
backend/routes/dashboard_routes.py
Rutas del panel principal con estadísticas y alertas
==============================================================
"""

from flask import Blueprint, render_template, jsonify
from flask_login import login_required
from backend.services.certificate_service import certificate_service

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
@login_required
def index():
    """Redirige al dashboard principal."""
    from flask import redirect, url_for
    return redirect(url_for("dashboard.panel"))


@dashboard_bp.route("/dashboard")
@login_required
def panel():
    """Panel principal con estadísticas y alertas."""
    # Actualizar estados antes de mostrar
    certificate_service.actualizar_todos_los_estados()

    stats = certificate_service.get_estadisticas()
    alertas = certificate_service.get_alertas()

    return render_template(
        "dashboard.html",
        stats=stats,
        alertas=alertas
    )


@dashboard_bp.route("/api/stats")
@login_required
def api_stats():
    """API JSON con estadísticas para Chart.js."""
    certificate_service.actualizar_todos_los_estados()
    stats = certificate_service.get_estadisticas()
    return jsonify(stats)
