"""
==============================================================
backend/routes/report_routes.py
Rutas para generación y descarga de reportes Excel
==============================================================
"""

from flask import Blueprint, request, send_file, flash, redirect, url_for
from flask_login import login_required
import io
from backend.models.certificado import Certificado
from backend.services.report_service import report_service
from datetime import datetime

report_bp = Blueprint("reportes", __name__, url_prefix="/reportes")


@report_bp.route("/excel/completo")
@login_required
def excel_completo():
    """Exporta todos los certificados a Excel."""
    try:
        certificados = Certificado.query.order_by(
            Certificado.fecha_vencimiento.asc()
        ).all()
        excel_bytes = report_service.exportar_excel_completo(certificados)
        filename = f"certificados_retie_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
        return send_file(
            io.BytesIO(excel_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f"Error al generar Excel: {str(e)}", "danger")
        return redirect(url_for("certificados.listar"))


@report_bp.route("/excel/vencimientos")
@login_required
def excel_vencimientos():
    """Exporta certificados próximos a vencer."""
    dias = request.args.get("dias", 90, type=int)
    try:
        excel_bytes = report_service.exportar_excel_vencimientos(dias)
        filename = f"vencimientos_{dias}dias_{datetime.now().strftime('%Y%m%d')}.xlsx"
        return send_file(
            io.BytesIO(excel_bytes),
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        flash(f"Error al generar reporte: {str(e)}", "danger")
        return redirect(url_for("dashboard.panel"))
