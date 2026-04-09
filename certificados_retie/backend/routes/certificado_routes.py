"""
==============================================================
backend/routes/certificado_routes.py
Rutas CRUD para certificados: crear, listar, editar, eliminar
==============================================================
"""

import os
import json
from flask import (
    Blueprint, render_template, redirect, url_for,
    request, flash, jsonify, send_from_directory,
    current_app, abort
)
from flask_login import login_required, current_user
from backend.database import db
from backend.models.certificado import Certificado
from backend.services.certificate_service import certificate_service
from backend.utils.validators import admin_required

cert_bp = Blueprint("certificados", __name__, url_prefix="/certificados")


# ── LISTAR ─────────────────────────────────────────────────

@cert_bp.route("/")
@login_required
def listar():
    """Lista todos los certificados con filtros y paginación."""
    # Actualizar estados automáticamente
    certificate_service.actualizar_todos_los_estados()

    # Parámetros de filtro
    filtros = {
        "numero_certificado": request.args.get("numero_certificado", ""),
        "producto": request.args.get("producto", ""),
        "organismo": request.args.get("organismo", ""),
        "estado": request.args.get("estado", "todos"),
        "fecha_venc_desde": request.args.get("fecha_venc_desde", ""),
        "fecha_venc_hasta": request.args.get("fecha_venc_hasta", ""),
        "texto": request.args.get("texto", ""),
    }
    page = request.args.get("page", 1, type=int)
    per_page = current_app.config.get("ITEMS_PER_PAGE", 20)

    paginacion = certificate_service.buscar_certificados(filtros, page, per_page)

    return render_template(
        "certificados.html",
        certificados=paginacion.items,
        paginacion=paginacion,
        filtros=filtros,
        total=paginacion.total
    )


# ── CREAR ──────────────────────────────────────────────────

@cert_bp.route("/nuevo", methods=["GET", "POST"])
@login_required
def nuevo():
    """Formulario para crear un nuevo certificado."""
    if request.method == "POST":
        datos = {
            "numero_certificado": request.form.get("numero_certificado", "").strip(),
            "convenio": request.form.get("convenio", "").strip(),
            "producto": request.form.get("producto", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip(),
            "organismo_certificador": request.form.get("organismo_certificador", "").strip(),
            "fecha_emision": request.form.get("fecha_emision", "").strip(),
            "fecha_vencimiento": request.form.get("fecha_vencimiento", "").strip(),
            "notas": request.form.get("notas", "").strip(),
        }

        # Validaciones básicas
        if not datos["numero_certificado"]:
            flash("El número de certificado es requerido.", "danger")
            return render_template("crear_certificado.html", datos=datos)
        if not datos["producto"]:
            flash("El producto es requerido.", "danger")
            return render_template("crear_certificado.html", datos=datos)
        if not datos["organismo_certificador"]:
            flash("El organismo certificador es requerido.", "danger")
            return render_template("crear_certificado.html", datos=datos)

        # Verificar duplicado
        if Certificado.query.filter_by(numero_certificado=datos["numero_certificado"]).first():
            flash(f"Ya existe un certificado con el número {datos['numero_certificado']}.", "warning")
            return render_template("crear_certificado.html", datos=datos)

        # Archivo PDF
        pdf_file = request.files.get("archivo_pdf")

        try:
            cert, ocr_resultado = certificate_service.crear_certificado(
                datos=datos,
                pdf_file=pdf_file if pdf_file and pdf_file.filename else None,
                pdf_folder=current_app.config["PDF_FOLDER"],
                images_folder=current_app.config["IMAGES_FOLDER"],
                usuario_id=current_user.id
            )

            # Mensaje con resultado OCR
            if ocr_resultado.get("datos_extraidos"):
                flash(
                    f"Certificado creado. OCR detectó información automáticamente "
                    f"(confianza: {int(ocr_resultado.get('confianza', 0) * 100)}%).",
                    "success"
                )
            else:
                flash("Certificado registrado exitosamente.", "success")

            return redirect(url_for("certificados.detalle", cert_id=cert.id))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear el certificado: {str(e)}", "danger")
            return render_template("crear_certificado.html", datos=datos)

    return render_template("crear_certificado.html", datos={})


# ── DETALLE ────────────────────────────────────────────────

@cert_bp.route("/<int:cert_id>")
@login_required
def detalle(cert_id):
    """Vista detallada de un certificado."""
    cert = Certificado.query.get_or_404(cert_id)
    cert.actualizar_estado()
    return render_template("detalle_certificado.html", cert=cert)


# ── EDITAR ─────────────────────────────────────────────────

@cert_bp.route("/<int:cert_id>/editar", methods=["GET", "POST"])
@login_required
def editar(cert_id):
    """Formulario para editar un certificado existente."""
    cert = Certificado.query.get_or_404(cert_id)

    if request.method == "POST":
        datos = {
            "numero_certificado": request.form.get("numero_certificado", "").strip(),
            "convenio": request.form.get("convenio", "").strip(),
            "producto": request.form.get("producto", "").strip(),
            "descripcion": request.form.get("descripcion", "").strip(),
            "organismo_certificador": request.form.get("organismo_certificador", "").strip(),
            "fecha_emision": request.form.get("fecha_emision", "").strip(),
            "fecha_vencimiento": request.form.get("fecha_vencimiento", "").strip(),
            "notas": request.form.get("notas", "").strip(),
        }

        pdf_file = request.files.get("archivo_pdf")

        try:
            cert = certificate_service.actualizar_certificado(
                cert_id=cert_id,
                datos=datos,
                pdf_file=pdf_file if pdf_file and pdf_file.filename else None,
                pdf_folder=current_app.config["PDF_FOLDER"],
                images_folder=current_app.config["IMAGES_FOLDER"],
            )
            flash("Certificado actualizado exitosamente.", "success")
            return redirect(url_for("certificados.detalle", cert_id=cert.id))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {str(e)}", "danger")

    return render_template("editar_certificado.html", cert=cert)


# ── ELIMINAR ───────────────────────────────────────────────

@cert_bp.route("/<int:cert_id>/eliminar", methods=["POST"])
@login_required
@admin_required
def eliminar(cert_id):
    """Elimina un certificado (solo ADMIN)."""
    eliminado = certificate_service.eliminar_certificado(
        cert_id, current_app.config["PDF_FOLDER"]
    )
    if eliminado:
        flash("Certificado eliminado correctamente.", "success")
    else:
        flash("No se encontró el certificado.", "warning")
    return redirect(url_for("certificados.listar"))


# ── VER / DESCARGAR PDF ────────────────────────────────────

@cert_bp.route("/<int:cert_id>/pdf")
@login_required
def ver_pdf(cert_id):
    """Sirve el archivo PDF de un certificado para visualización."""
    cert = Certificado.query.get_or_404(cert_id)
    if not cert.archivo_pdf:
        abort(404)
    return send_from_directory(
        current_app.config["PDF_FOLDER"],
        cert.archivo_pdf,
        as_attachment=False,
        mimetype="application/pdf"
    )


@cert_bp.route("/<int:cert_id>/descargar")
@login_required
def descargar_pdf(cert_id):
    """Descarga el PDF de un certificado."""
    cert = Certificado.query.get_or_404(cert_id)
    if not cert.archivo_pdf:
        abort(404)
    return send_from_directory(
        current_app.config["PDF_FOLDER"],
        cert.archivo_pdf,
        as_attachment=True,
        download_name=f"certificado_{cert.numero_certificado}.pdf"
    )


# ── API JSON ───────────────────────────────────────────────

@cert_bp.route("/api/buscar")
@login_required
def api_buscar():
    """API de búsqueda rápida para autocompletado."""
    q = request.args.get("q", "")
    if len(q) < 2:
        return jsonify([])
    certs = Certificado.query.filter(
        db.or_(
            Certificado.numero_certificado.ilike(f"%{q}%"),
            Certificado.producto.ilike(f"%{q}%"),
        )
    ).limit(10).all()
    return jsonify([{
        "id": c.id,
        "numero": c.numero_certificado,
        "producto": c.producto,
        "estado": c.estado_certificado,
    } for c in certs])


@cert_bp.route("/api/<int:cert_id>")
@login_required
def api_detalle(cert_id):
    """API JSON para detalle de certificado."""
    cert = Certificado.query.get_or_404(cert_id)
    return jsonify(cert.to_dict())
