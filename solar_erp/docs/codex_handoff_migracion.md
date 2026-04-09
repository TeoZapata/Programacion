# Handoff Para Otra Ventana De Codex

## Contexto

El proyecto actual es `GeoInventario`, una aplicacion de escritorio en Python con PySide/Qt.

Se decidio planear una migracion a una version web moderna porque la UI actual presenta bloqueos y la arquitectura de escritorio ya esta dificultando crecimiento y mantenimiento.

## Objetivo De La Nueva Version

Construir una nueva aplicacion web de GeoInventario con:

- backend en `FastAPI`
- ORM `SQLAlchemy`
- migraciones con `Alembic`
- frontend en `React + TypeScript + Vite`
- base de datos `PostgreSQL` como objetivo final

## Modulos Que Deben Migrarse

1. usuarios y autenticacion
2. clientes
3. proyectos
4. proveedores
5. inventario de materiales
6. movimientos de inventario
7. pedidos de material
8. trabajadores
9. herramientas
10. historial de herramientas
11. dashboard
12. reportes PDF

## Problemas Del Sistema Actual Que Motivaron La Migracion

- bloqueos en UI al trabajar con tablas grandes
- logica de negocio mezclada con vistas
- busquedas y repintado poco optimizados
- archivos de UI demasiado grandes
- dificultad para crecimiento multiusuario

## Criterios Para La Nueva Arquitectura

- separacion clara entre frontend, backend y base de datos
- APIs limpias
- reglas de negocio fuera de la UI
- historial y auditoria desde backend
- consultas paginadas y filtros con debounce
- tablas virtualizadas o render eficiente

## Alcance Del Primer MVP

Debe incluir:

- login
- inventario de materiales
- movimientos
- pedidos
- herramientas
- historial de herramientas

## Estructura Sugerida Del Nuevo Repo

```text
geoinventario-web/
  backend/
    app/
      api/
      core/
      db/
      models/
      schemas/
      services/
      repositories/
      reports/
    alembic/
    tests/
  frontend/
    src/
      app/
      components/
      features/
      pages/
      services/
      types/
```

## Forma Correcta De Continuar En Otra Ventana

Pedir a la nueva ventana de Codex que:

1. lea este archivo
2. lea `docs/migracion_web_plan.md`
3. proponga el scaffold inicial del nuevo proyecto
4. cree primero la base del `backend/` y `frontend/`
5. no toque el proyecto PySide actual salvo lectura

## Prompt Recomendado Para La Siguiente Ventana

```text
Lee `docs/codex_handoff_migracion.md` y `docs/migracion_web_plan.md`.
Quiero iniciar la nueva version web de GeoInventario en un nuevo workspace o en una carpeta hermana.

Objetivo:
- backend con FastAPI + SQLAlchemy + Alembic
- frontend con React + TypeScript + Vite
- estructura limpia por modulos

Empieza creando el scaffold base del proyecto, define la estructura de carpetas, dependencias iniciales, configuracion base y primer modelo de usuarios/autenticacion.

No modifiques la app PySide actual salvo que sea necesario leerla como referencia.
```

## Recomendacion De Trabajo

No intentar migrar todo en una sola sesion.

Dividir el trabajo asi:

1. scaffold backend/frontend
2. auth y usuarios
3. inventario
4. movimientos
5. pedidos
6. herramientas
7. historial
8. reportes
9. migracion de datos

## Nota Importante Sobre Contexto

Para pasar informacion entre ventanas de Codex, la forma mas confiable no es “la memoria” de la sesion sino archivos concretos dentro del repo.

Por eso este handoff debe mantenerse actualizado a medida que avance la migracion.
