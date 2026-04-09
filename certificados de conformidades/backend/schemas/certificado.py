from datetime import date, datetime

from pydantic import BaseModel, Field


class CertificadoBase(BaseModel):
    numero_certificado: str = Field(..., max_length=100)
    convenio: str | None = Field(None, max_length=150)
    producto: str = Field(..., max_length=200)
    descripcion: str | None = None
    organismo_certificador: str = Field(..., max_length=200)
    fecha_emision: date | None = None
    fecha_vencimiento: date | None = None


class CertificadoCreate(CertificadoBase):
    pass


class CertificadoUpdate(BaseModel):
    numero_certificado: str | None = Field(None, max_length=100)
    convenio: str | None = Field(None, max_length=150)
    producto: str | None = Field(None, max_length=200)
    descripcion: str | None = None
    organismo_certificador: str | None = Field(None, max_length=200)
    fecha_emision: date | None = None
    fecha_vencimiento: date | None = None


class CertificadoRead(BaseModel):
    id: int
    numero_certificado: str
    convenio: str | None
    producto: str
    descripcion: str | None
    organismo_certificador: str
    fecha_emision: date | None
    fecha_vencimiento: date | None
    fecha_registro: datetime
    archivo_pdf: str
    imagen_extraida: str | None
    estado_certificado: str

    class Config:
        from_attributes = True

