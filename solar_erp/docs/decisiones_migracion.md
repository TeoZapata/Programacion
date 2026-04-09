# Decisiones Iniciales De Migracion

## Decision 1

No reescribir en C.

Motivo:

- complejidad muy alta
- poco retorno para un ERP/inventario
- menor velocidad de desarrollo

## Decision 2

Preferir arquitectura web frente a otra app de escritorio.

Motivo:

- mejor experiencia multiusuario
- despliegue mas flexible
- UI moderna mas facil
- mejor separacion de responsabilidades

## Decision 3

Usar `FastAPI + SQLAlchemy + Alembic`.

Motivo:

- stack moderno
- facil de estructurar
- APIs limpias
- buena integracion con frontend moderno

## Decision 4

Usar `React + TypeScript + Vite` como ruta principal.

Motivo:

- ecosistema amplio
- buenas tablas, formularios y estado
- soporte fuerte para aplicaciones administrativas

## Decision 5

Mantener el proyecto actual solo como referencia funcional hasta completar el reemplazo.

Motivo:

- reduce riesgo
- permite comparar salidas
- facilita migracion gradual de datos y reglas de negocio
