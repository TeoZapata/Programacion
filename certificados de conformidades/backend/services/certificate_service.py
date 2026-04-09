from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..models.certificado import Certificado
from ..models.certificado_historial import CertificadoHistorial
from ..schemas.certificado import CertificadoCreate, CertificadoUpdate
from ..utils.validators import validate_fecha_rango


def calcular_estado(fecha_vencimiento: date | None) -> str:
    if not fecha_vencimiento:
        return "vigente"

    hoy = date.today()
    if fecha_vencimiento < hoy:
        return "vencido"
    if fecha_vencimiento <= hoy + timedelta(days=60):
        return "por_vencer"
    return "vigente"


def registrar_historial(
    db: Session,
    certificado_id: int,
    usuario_id: int | None,
    accion: str,
    cambios: dict[str, Any] | None = None,
) -> None:
    historial = CertificadoHistorial(
        certificado_id=certificado_id,
        usuario_id=usuario_id,
        accion=accion,
        cambios=cambios,
        fecha=datetime.utcnow(),
    )
    db.add(historial)


def crear_certificado(
    db: Session,
    data: CertificadoCreate,
    archivo_pdf: str,
    imagen_extraida: str | None,
    usuario_id: int | None,
) -> Certificado:
    validate_fecha_rango(data.fecha_emision, data.fecha_vencimiento)
    estado = calcular_estado(data.fecha_vencimiento)

    certificado = Certificado(
        numero_certificado=data.numero_certificado,
        convenio=data.convenio,
        producto=data.producto,
        descripcion=data.descripcion,
        organismo_certificador=data.organismo_certificador,
        fecha_emision=data.fecha_emision,
        fecha_vencimiento=data.fecha_vencimiento,
        archivo_pdf=archivo_pdf,
        imagen_extraida=imagen_extraida,
        estado_certificado=estado,
    )
    db.add(certificado)
    db.flush()

    registrar_historial(
        db,
        certificado_id=certificado.id,
        usuario_id=usuario_id,
        accion="CREAR",
        cambios=data.model_dump(),
    )

    return certificado


def actualizar_certificado(
    db: Session,
    certificado: Certificado,
    data: CertificadoUpdate,
    usuario_id: int | None,
) -> Certificado:
    validate_fecha_rango(data.fecha_emision or certificado.fecha_emision, data.fecha_vencimiento or certificado.fecha_vencimiento)

    cambios: dict[str, Any] = {}

    for field, value in data.model_dump(exclude_unset=True).items():
        valor_anterior = getattr(certificado, field)
        if valor_anterior != value:
            cambios[field] = {"antes": valor_anterior, "despues": value}
            setattr(certificado, field, value)

    certificado.estado_certificado = calcular_estado(certificado.fecha_vencimiento)

    if cambios:
        registrar_historial(
            db,
            certificado_id=certificado.id,
            usuario_id=usuario_id,
            accion="ACTUALIZAR",
            cambios=cambios,
        )

    return certificado


def eliminar_certificado(
    db: Session,
    certificado: Certificado,
    usuario_id: int | None,
) -> None:
    registrar_historial(
        db,
        certificado_id=certificado.id,
        usuario_id=usuario_id,
        accion="ELIMINAR",
        cambios=None,
    )
    db.delete(certificado)


def obtener_resumen_dashboard(db: Session) -> dict[str, Any]:
    total = db.scalar(select(func.count(Certificado.id))) or 0

    vigentes = db.scalar(
        select(func.count(Certificado.id)).where(Certificado.estado_certificado == "vigente")
    ) or 0
    por_vencer = db.scalar(
        select(func.count(Certificado.id)).where(Certificado.estado_certificado == "por_vencer")
    ) or 0
    vencidos = db.scalar(
        select(func.count(Certificado.id)).where(Certificado.estado_certificado == "vencido")
    ) or 0

    certificados_por_producto_rows = db.execute(
        select(Certificado.producto, func.count(Certificado.id)).group_by(Certificado.producto)
    ).all()
    certificados_por_producto = {row[0]: row[1] for row in certificados_por_producto_rows}

    certificados_por_organismo_rows = db.execute(
        select(
            Certificado.organismo_certificador,
            func.count(Certificado.id),
        ).group_by(Certificado.organismo_certificador)
    ).all()
    certificados_por_organismo = {row[0]: row[1] for row in certificados_por_organismo_rows}

    hoy = date.today()
    fecha_limite = hoy + timedelta(days=365)
    vencimientos_rows = db.execute(
        select(
            func.strftime("%Y-%m", Certificado.fecha_vencimiento)
            if db.bind.dialect.name == "sqlite"
            else func.to_char(Certificado.fecha_vencimiento, "YYYY-MM"),
            func.count(Certificado.id),
        )
        .where(
            Certificado.fecha_vencimiento.is_not(None),
            Certificado.fecha_vencimiento >= hoy,
            Certificado.fecha_vencimiento <= fecha_limite,
        )
        .group_by(1)
        .order_by(1)
    ).all()
    vencimientos_por_mes = {row[0]: row[1] for row in vencimientos_rows}

    return {
        "total_certificados": total,
        "vigentes": vigentes,
        "por_vencer": por_vencer,
        "vencidos": vencidos,
        "certificados_por_producto": certificados_por_producto,
        "certificados_por_organismo": certificados_por_organismo,
        "vencimientos_por_mes": vencimientos_por_mes,
    }

