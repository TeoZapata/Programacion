from datetime import date

from fastapi import HTTPException, status


def validate_fecha_rango(
    fecha_emision: date | None,
    fecha_vencimiento: date | None,
) -> None:
    if fecha_emision and fecha_vencimiento and fecha_emision > fecha_vencimiento:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha de emisión no puede ser posterior a la fecha de vencimiento",
        )

