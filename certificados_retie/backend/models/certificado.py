"""
==============================================================
backend/models/certificado.py
Modelo de Certificado RETIE con control de estados y fechas
==============================================================
"""

from backend.database import db
from datetime import datetime, date, timedelta
from sqlalchemy import Index


class Certificado(db.Model):
    """Modelo principal de certificado de conformidad RETIE."""

    __tablename__ = "certificados"

    # ── Identificadores ────────────────────────────────────
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    numero_certificado = db.Column(db.String(100), unique=True, nullable=False)
    convenio = db.Column(db.String(200), nullable=True)

    # ── Información del producto ───────────────────────────
    producto = db.Column(db.String(200), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    organismo_certificador = db.Column(db.String(200), nullable=False)

    # ── Fechas ─────────────────────────────────────────────
    fecha_emision = db.Column(db.Date, nullable=True)
    fecha_vencimiento = db.Column(db.Date, nullable=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_modificacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # ── Archivos ───────────────────────────────────────────
    archivo_pdf = db.Column(db.String(300), nullable=True)  # ruta relativa del PDF
    imagen_extraida = db.Column(db.String(300), nullable=True)  # ruta de la imagen OCR

    # ── Estado ─────────────────────────────────────────────
    estado_certificado = db.Column(
        db.String(20), nullable=False, default="vigente"
    )
    # Valores: 'vigente', 'por_vencer', 'vencido'

    # ── OCR / IA ───────────────────────────────────────────
    texto_ocr = db.Column(db.Text, nullable=True)       # texto bruto extraído por OCR
    datos_ia = db.Column(db.Text, nullable=True)        # JSON con datos detectados por IA
    confianza_ocr = db.Column(db.Float, nullable=True)  # % de confianza del OCR

    # ── Auditoría ──────────────────────────────────────────
    usuario_id = db.Column(db.Integer, db.ForeignKey("usuarios.id"), nullable=True)
    notas = db.Column(db.Text, nullable=True)

    # ── Índices para búsqueda rápida ───────────────────────
    __table_args__ = (
        Index("idx_numero_cert", "numero_certificado"),
        Index("idx_producto", "producto"),
        Index("idx_fecha_venc", "fecha_vencimiento"),
        Index("idx_estado", "estado_certificado"),
        Index("idx_organismo", "organismo_certificador"),
    )

    # ── Propiedades calculadas ─────────────────────────────

    @property
    def dias_para_vencer(self) -> int | None:
        """Días que faltan para el vencimiento (negativo = ya venció)."""
        if not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - date.today()
        return delta.days

    @property
    def estado_calculado(self) -> str:
        """Calcula el estado real basado en fechas actuales."""
        dias = self.dias_para_vencer
        if dias is None:
            return "vigente"
        if dias < 0:
            return "vencido"
        if dias <= 30:
            return "por_vencer"
        return "vigente"

    @property
    def alerta_nivel(self) -> str:
        """Nivel de alerta: 'danger', 'warning', 'info', 'success'."""
        dias = self.dias_para_vencer
        if dias is None:
            return "secondary"
        if dias < 0:
            return "danger"
        if dias <= 30:
            return "danger"
        if dias <= 60:
            return "warning"
        if dias <= 90:
            return "info"
        return "success"

    # ── Método para actualizar estado ──────────────────────

    def actualizar_estado(self):
        """Actualiza el campo estado_certificado según las fechas."""
        self.estado_certificado = self.estado_calculado

    # ── Serialización ─────────────────────────────────────

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "numero_certificado": self.numero_certificado,
            "convenio": self.convenio,
            "producto": self.producto,
            "descripcion": self.descripcion,
            "organismo_certificador": self.organismo_certificador,
            "fecha_emision": self.fecha_emision.strftime("%Y-%m-%d") if self.fecha_emision else None,
            "fecha_vencimiento": self.fecha_vencimiento.strftime("%Y-%m-%d") if self.fecha_vencimiento else None,
            "fecha_registro": self.fecha_registro.strftime("%Y-%m-%d %H:%M") if self.fecha_registro else None,
            "archivo_pdf": self.archivo_pdf,
            "imagen_extraida": self.imagen_extraida,
            "estado_certificado": self.estado_certificado,
            "dias_para_vencer": self.dias_para_vencer,
            "alerta_nivel": self.alerta_nivel,
            "notas": self.notas,
        }

    def to_dict_full(self) -> dict:
        """Versión completa incluyendo texto OCR."""
        d = self.to_dict()
        d["texto_ocr"] = self.texto_ocr
        d["confianza_ocr"] = self.confianza_ocr
        return d

    def __repr__(self):
        return f"<Certificado {self.numero_certificado} - {self.producto}>"
