from datetime import datetime

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    csrf_token: str


class TokenData(BaseModel):
    user_id: int | None = None
    usuario: str | None = None
    rol: str | None = None
    exp: int | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class SessionUser(BaseModel):
    id: int
    nombre: str
    usuario: str
    correo: str
    rol: str
    activo: bool
    fecha_creacion: datetime

