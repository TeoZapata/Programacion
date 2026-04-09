from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    nombre: str = Field(..., max_length=150)
    correo: EmailStr
    usuario: str = Field(..., max_length=50)
    rol: str = Field(..., pattern="^(ADMIN|USUARIO)$")
    activo: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    nombre: str | None = Field(None, max_length=150)
    correo: EmailStr | None = None
    rol: str | None = Field(None, pattern="^(ADMIN|USUARIO)$")
    activo: bool | None = None
    password: str | None = Field(None, min_length=6)


class UserRead(BaseModel):
    id: int
    nombre: str
    correo: EmailStr
    usuario: str
    rol: str
    activo: bool
    fecha_creacion: datetime

    class Config:
        from_attributes = True

