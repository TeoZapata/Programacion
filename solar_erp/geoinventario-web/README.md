# GeoInventario Web

Nueva base del proyecto web para la migracion de GeoInventario.

## Estructura

```text
geoinventario-web/
  backend/
  frontend/
```

## Stack

- Backend: FastAPI + SQLAlchemy + Alembic
- Frontend: React + TypeScript + Vite
- Base de datos objetivo: PostgreSQL

## Estado

Este scaffold crea la base inicial del monorepo sin tocar la aplicacion de escritorio actual.

## Siguientes pasos

1. Crear y activar un entorno virtual para `backend/`
2. Instalar dependencias Python con `pip install -e .`
3. Instalar Node.js y luego dependencias del frontend con `npm install`
4. Implementar el modulo de autenticacion y usuarios
