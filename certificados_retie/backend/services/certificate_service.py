"""
==============================================================
backend/services/certificate_service.py
Lógica de negocio para gestión de certificados RETIE
==============================================================
"""

import os
import json
import logging
from datetime import date, datetime
from pathlib import Path

from backend.database import db
from backend.models.certificado import Certificado
from backend.services.ocr_service import ocr_service
from backend.utils.validators import validar_extension_pdf

logger = logging.getLogger(__name__)


class CertificateService:
    """Servicio centralizado para operaciones sobre certificados."""

    # ── CRUD ───────────────────────────────────────────────

    def crear_certificado(self, datos: dict, pdf_file=None,
                          pdf_folder: str = "", images_folder: str = "",
                          usuario_id: int = None) -> tuple[Certificado, dict]:
        """
        Crea un nuevo certificado.

        Args:
            datos: dict con los campos del formulario
            pdf_file: archivo PDF subido (FileStorage)
            pdf_folder: ruta donde guardar PDFs
            images_folder: ruta donde guardar imágenes OCR
            usuario_id: ID del usuario que registra

        Returns:
            (Certificado, ocr_resultado)
        """
        ocr_resultado = {}

        # 1. Guardar archivo PDF si se proporcionó
        pdf_path = None
        pdf_filename = None
        if pdf_file and validar_extension_pdf(pdf_file.filename):
            from werkzeug.utils import secure_filename
            import time
            timestamp = int(time.time())
            pdf_filename = f"{timestamp}_{secure_filename(pdf_file.filename)}"
            pdf_path = os.path.join(pdf_folder, pdf_filename)
            os.makedirs(pdf_folder, exist_ok=True)
            pdf_file.save(pdf_path)

        # 2. Procesar OCR si hay PDF
        if pdf_path and os.path.exists(pdf_path):
            try:
                ocr_resultado = ocr_service.procesar_pdf(pdf_path, images_folder)
                # Completar campos vacíos con datos OCR
                extracted = ocr_resultado.get("datos_extraidos", {})
                for campo in ["numero_certificado", "organismo_certificador",
                               "producto", "fecha_emision", "fecha_vencimiento"]:
                    if not datos.get(campo) and extracted.get(campo):
                        datos[campo] = extracted[campo]
            except Exception as e:
                logger.warning(f"OCR falló (no crítico): {e}")

        # 3. Crear objeto certificado
        cert = Certificado(
            numero_certificado=datos.get("numero_certificado", "").strip(),
            convenio=datos.get("convenio", "").strip() or None,
            producto=datos.get("producto", "").strip(),
            descripcion=datos.get("descripcion", "").strip() or None,
            organismo_certificador=datos.get("organismo_certificador", "").strip(),
            fecha_emision=self._parse_date(datos.get("fecha_emision")),
            fecha_vencimiento=self._parse_date(datos.get("fecha_vencimiento")),
            archivo_pdf=pdf_filename,
            imagen_extraida=os.path.basename(ocr_resultado.get("imagen_path") or "") or None,
            texto_ocr=ocr_resultado.get("texto_ocr", "")[:10000],  # Limitar tamaño
            confianza_ocr=ocr_resultado.get("confianza", 0.0),
            notas=datos.get("notas", "").strip() or None,
            usuario_id=usuario_id,
        )

        # 4. Calcular estado inicial
        cert.actualizar_estado()

        db.session.add(cert)
        db.session.commit()

        return cert, ocr_resultado

    def actualizar_certificado(self, cert_id: int, datos: dict,
                                pdf_file=None, pdf_folder: str = "",
                                images_folder: str = "") -> Certificado:
        """Actualiza un certificado existente."""
        cert = Certificado.query.get_or_404(cert_id)

        # Actualizar campos
        if datos.get("numero_certificado"):
            cert.numero_certificado = datos["numero_certificado"].strip()
        cert.convenio = datos.get("convenio", "").strip() or None
        cert.producto = datos.get("producto", cert.producto).strip()
        cert.descripcion = datos.get("descripcion", "").strip() or None
        cert.organismo_certificador = datos.get("organismo_certificador", cert.organismo_certificador).strip()
        cert.fecha_emision = self._parse_date(datos.get("fecha_emision")) or cert.fecha_emision
        cert.fecha_vencimiento = self._parse_date(datos.get("fecha_vencimiento")) or cert.fecha_vencimiento
        cert.notas = datos.get("notas", "").strip() or None
        cert.fecha_modificacion = datetime.utcnow()

        # Actualizar PDF si se subió uno nuevo
        if pdf_file and validar_extension_pdf(pdf_file.filename):
            from werkzeug.utils import secure_filename
            import time
            timestamp = int(time.time())
            pdf_filename = f"{timestamp}_{secure_filename(pdf_file.filename)}"
            pdf_path = os.path.join(pdf_folder, pdf_filename)
            os.makedirs(pdf_folder, exist_ok=True)
            pdf_file.save(pdf_path)
            cert.archivo_pdf = pdf_filename

        # Recalcular estado
        cert.actualizar_estado()
        db.session.commit()
        return cert

    def eliminar_certificado(self, cert_id: int, pdf_folder: str = "") -> bool:
        """Elimina un certificado y su PDF asociado."""
        cert = Certificado.query.get(cert_id)
        if not cert:
            return False
        # Eliminar archivo físico
        if cert.archivo_pdf:
            pdf_path = os.path.join(pdf_folder, cert.archivo_pdf)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        db.session.delete(cert)
        db.session.commit()
        return True

    # ── BÚSQUEDA Y FILTRADO ────────────────────────────────

    def buscar_certificados(self, filtros: dict, page: int = 1,
                             per_page: int = 20) -> object:
        """
        Búsqueda avanzada con filtros múltiples y paginación.

        filtros: {
            numero_certificado, producto, organismo,
            estado, fecha_venc_desde, fecha_venc_hasta, texto
        }
        """
        query = Certificado.query

        if filtros.get("numero_certificado"):
            query = query.filter(
                Certificado.numero_certificado.ilike(f"%{filtros['numero_certificado']}%")
            )
        if filtros.get("producto"):
            query = query.filter(
                Certificado.producto.ilike(f"%{filtros['producto']}%")
            )
        if filtros.get("organismo"):
            query = query.filter(
                Certificado.organismo_certificador.ilike(f"%{filtros['organismo']}%")
            )
        if filtros.get("estado") and filtros["estado"] != "todos":
            query = query.filter(
                Certificado.estado_certificado == filtros["estado"]
            )
        if filtros.get("fecha_venc_desde"):
            query = query.filter(
                Certificado.fecha_vencimiento >= self._parse_date(filtros["fecha_venc_desde"])
            )
        if filtros.get("fecha_venc_hasta"):
            query = query.filter(
                Certificado.fecha_vencimiento <= self._parse_date(filtros["fecha_venc_hasta"])
            )
        if filtros.get("texto"):
            t = f"%{filtros['texto']}%"
            query = query.filter(
                db.or_(
                    Certificado.numero_certificado.ilike(t),
                    Certificado.producto.ilike(t),
                    Certificado.organismo_certificador.ilike(t),
                    Certificado.descripcion.ilike(t),
                )
            )

        query = query.order_by(Certificado.fecha_vencimiento.asc())
        return query.paginate(page=page, per_page=per_page, error_out=False)

    # ── ESTADÍSTICAS PARA DASHBOARD ────────────────────────

    def get_estadisticas(self) -> dict:
        """Retorna estadísticas completas para el dashboard."""
        hoy = date.today()
        from datetime import timedelta

        total = Certificado.query.count()
        vigentes = Certificado.query.filter(
            Certificado.estado_certificado == "vigente"
        ).count()
        vencidos = Certificado.query.filter(
            Certificado.estado_certificado == "vencido"
        ).count()
        por_vencer = Certificado.query.filter(
            Certificado.estado_certificado == "por_vencer"
        ).count()

        # Por vencer en 30/60/90 días
        alerta_30 = Certificado.query.filter(
            Certificado.fecha_vencimiento.between(hoy, hoy + timedelta(days=30))
        ).count()
        alerta_60 = Certificado.query.filter(
            Certificado.fecha_vencimiento.between(hoy + timedelta(days=31), hoy + timedelta(days=60))
        ).count()
        alerta_90 = Certificado.query.filter(
            Certificado.fecha_vencimiento.between(hoy + timedelta(days=61), hoy + timedelta(days=90))
        ).count()

        # Top productos (para gráfica)
        from sqlalchemy import func
        productos_query = db.session.query(
            Certificado.producto,
            func.count(Certificado.id).label("total")
        ).group_by(Certificado.producto).order_by(func.count(Certificado.id).desc()).limit(8).all()

        organismos_query = db.session.query(
            Certificado.organismo_certificador,
            func.count(Certificado.id).label("total")
        ).group_by(Certificado.organismo_certificador).order_by(func.count(Certificado.id).desc()).limit(6).all()

        # Vencimientos por mes (próximos 6 meses)
        venc_por_mes = []
        for i in range(6):
            mes_inicio = hoy.replace(day=1)
            if i > 0:
                import calendar
                for _ in range(i):
                    last_day = calendar.monthrange(mes_inicio.year, mes_inicio.month)[1]
                    mes_inicio = (mes_inicio.replace(day=last_day) + timedelta(days=1))
            mes_fin = mes_inicio.replace(
                day=__import__('calendar').monthrange(mes_inicio.year, mes_inicio.month)[1]
            )
            count = Certificado.query.filter(
                Certificado.fecha_vencimiento.between(mes_inicio, mes_fin)
            ).count()
            venc_por_mes.append({
                "mes": mes_inicio.strftime("%b %Y"),
                "total": count
            })

        return {
            "total": total,
            "vigentes": vigentes,
            "vencidos": vencidos,
            "por_vencer": por_vencer,
            "alerta_30": alerta_30,
            "alerta_60": alerta_60,
            "alerta_90": alerta_90,
            "productos": [{"producto": p.producto, "total": p.total} for p in productos_query],
            "organismos": [{"organismo": o.organismo_certificador, "total": o.total} for o in organismos_query],
            "vencimientos_por_mes": venc_por_mes,
        }

    def get_alertas(self) -> list:
        """Retorna certificados próximos a vencer ordenados por urgencia."""
        from datetime import timedelta
        hoy = date.today()
        return Certificado.query.filter(
            Certificado.fecha_vencimiento <= hoy + timedelta(days=90),
            Certificado.fecha_vencimiento >= hoy
        ).order_by(Certificado.fecha_vencimiento.asc()).limit(20).all()

    # ── UTILIDADES ─────────────────────────────────────────

    def actualizar_todos_los_estados(self):
        """Recalcula y actualiza el estado de TODOS los certificados."""
        certs = Certificado.query.all()
        for c in certs:
            c.actualizar_estado()
        db.session.commit()
        return len(certs)

    @staticmethod
    def _parse_date(valor) -> date | None:
        """Convierte string de fecha a objeto date."""
        if not valor:
            return None
        if isinstance(valor, date):
            return valor
        for fmt in ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y"]:
            try:
                return datetime.strptime(str(valor).strip(), fmt).date()
            except ValueError:
                continue
        return None


certificate_service = CertificateService()
