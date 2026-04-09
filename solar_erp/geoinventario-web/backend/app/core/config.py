from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "GeoInventario API"
    app_env: str = "development"
    api_v1_prefix: str = "/api/v1"
    secret_key: str = "change-me"
    access_token_expire_minutes: int = 60
    database_url: str = "sqlite:///./geoinventario.db"
    backend_cors_origins: str = "http://localhost:5173"
    first_superuser_email: str = "admin@geoinventario.local"
    first_superuser_name: str = "Administrador"
    first_superuser_password: str = "admin123"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


settings = Settings()
