from datetime import date

from pydantic import BaseModel


class DashboardSummary(BaseModel):
    total_certificados: int
    vigentes: int
    por_vencer: int
    vencidos: int

    certificados_por_producto: dict[str, int]
    certificados_por_organismo: dict[str, int]
    vencimientos_por_mes: dict[str, int]


class VencimientoFiltro(BaseModel):
    hasta_fecha: date

