# Backend

Base inicial del backend de GeoInventario Web.

## Capas

- `app/api`: routers y endpoints
- `app/core`: configuracion y seguridad
- `app/db`: sesion y base del ORM
- `app/models`: modelos SQLAlchemy
- `app/schemas`: contratos Pydantic
- `app/services`: logica de negocio
- `app/repositories`: acceso a datos
- `app/reports`: reportes PDF
- `tests`: pruebas

## Arranque esperado

```bash
uvicorn app.main:app --reload
```

## Auth inicial

Al iniciar por primera vez, la app crea un usuario administrador usando las variables:

- `FIRST_SUPERUSER_EMAIL`
- `FIRST_SUPERUSER_NAME`
- `FIRST_SUPERUSER_PASSWORD`
