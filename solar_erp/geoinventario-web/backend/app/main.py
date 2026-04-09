from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import SessionLocal, engine
from app.services.bootstrap import ensure_initial_user


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in settings.backend_cors_origins.split(",") if origin.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)

    @app.on_event("startup")
    def on_startup() -> None:
        Base.metadata.create_all(bind=engine)
        with SessionLocal() as session:
            ensure_initial_user(session)

    @app.get("/", tags=["meta"])
    def root() -> dict[str, str]:
        return {"message": f"{settings.app_name} running"}

    return app


app = create_application()
