import os
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"

if ENV_PATH.exists():
    load_dotenv(ENV_PATH)


class Settings(BaseModel):
    environment: str = os.getenv("ENVIRONMENT", "development")
    secret_key: str = os.getenv("SECRET_KEY", "change_me_in_production")
    algorithm: str = os.getenv("ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

    use_sqlite: bool = os.getenv("USE_SQLITE", "1") == "1"
    database_url_sqlite: str = os.getenv(
        "DATABASE_URL_SQLITE", f"sqlite:///{(BASE_DIR / 'certificados_retie.db').as_posix()}"
    )
    database_url_postgresql: str = os.getenv(
        "DATABASE_URL_POSTGRESQL",
        "postgresql+psycopg2://user:password@localhost:5432/certificados_retie",
    )

    upload_dir: Path = Path(os.getenv("UPLOAD_DIR", BASE_DIR / "uploads"))
    pdf_upload_dir: Path = Path(os.getenv("PDF_UPLOAD_DIR", BASE_DIR / "uploads" / "pdf"))
    image_upload_dir: Path = Path(os.getenv("IMAGE_UPLOAD_DIR", BASE_DIR / "uploads" / "images"))

    tesseract_cmd: str | None = os.getenv("TESSERACT_CMD")
    poppler_path: str | None = os.getenv("POPPLER_PATH")

    llm_api_url: str | None = os.getenv("LLM_API_URL")
    llm_api_key: str | None = os.getenv("LLM_API_KEY")

    backup_dir: Path = Path(os.getenv("BACKUP_DIR", BASE_DIR / "backups"))

    @property
    def database_url(self) -> str:
        return self.database_url_sqlite if self.use_sqlite else self.database_url_postgresql


@lru_cache
def get_settings() -> Settings:
    settings = Settings()

    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.pdf_upload_dir.mkdir(parents=True, exist_ok=True)
    settings.image_upload_dir.mkdir(parents=True, exist_ok=True)
    settings.backup_dir.mkdir(parents=True, exist_ok=True)

    return settings

