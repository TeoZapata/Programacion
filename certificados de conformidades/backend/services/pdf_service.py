from pathlib import Path
from typing import BinaryIO

from ..config import get_settings


settings = get_settings()


def guardar_pdf(file_obj: BinaryIO, filename: str) -> Path:
    destino = settings.pdf_upload_dir / filename
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "wb") as f:
        while True:
            chunk = file_obj.read(1024 * 1024)
            if not chunk:
                break:
            f.write(chunk)
    return destino


def guardar_imagen_preview(contenido: bytes, filename: str) -> Path:
    destino = settings.image_upload_dir / filename
    destino.parent.mkdir(parents=True, exist_ok=True)
    with open(destino, "wb") as f:
        f.write(contenido)
    return destino

