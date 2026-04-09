from datetime import date, timedelta

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from ..models.certificado import Certificado


def obtener_alertas_vencimiento(db: Session) -> dict[str, list[Certificado]]:
    hoy = date.today()
    rangos = {
        "30": (hoy, hoy + timedelta(days=30)),
        "60": (hoy + timedelta(days=31), hoy + timedelta(days=60)),
        "90": (hoy + timedelta(days=61), hoy + timedelta(days=90)),
    }

    alertas: dict[str, list[Certificado]] = {"30": [], "60": [], "90": []}

    for clave, (inicio, fin) in rangos.items():
        resultados = (
            db.execute(
                select(Certificado).where(
                    and_(
                        Certificado.fecha_vencimiento.is_not(None),
                        Certificado.fecha_vencimiento >= inicio,
                        Certificado.fecha_vencimiento <= fin,
                    )
                )
            )
            .scalars()
            .all()
        )
        alertas[clave] = resultados

    return alertas

