# Plan De Migracion Web: GeoInventario

## Objetivo

Crear una nueva version de GeoInventario como aplicacion web moderna, mas estable y escalable, manteniendo la logica de inventario actual pero mejorando:

- rendimiento de interfaz
- mantenibilidad
- soporte multiusuario
- trazabilidad e historial
- capacidad de despliegue en red local o internet

## Recomendacion Tecnica

### Stack sugerido

- Backend: `FastAPI`
- ORM: `SQLAlchemy`
- Migraciones: `Alembic`
- Base de datos:
  - desarrollo inicial: `SQLite`
  - produccion o multiusuario real: `PostgreSQL`
- Frontend:
  - opcion recomendada: `React + Vite + TypeScript`
  - opcion valida: `Vue 3 + Vite + TypeScript`
- UI:
  - `shadcn/ui` o componentes equivalentes si se usa React
  - tablas virtualizadas para listados grandes
- Autenticacion:
  - sesiones o JWT con refresh, segun despliegue
- Reportes:
  - PDF desde backend
- Empaquetado:
  - local/red interna: `Docker Compose`
  - escritorio opcional: `Tauri` consumiendo la app web

## Por Que Esta Ruta

- El problema actual no es solo Python, sino una UI de escritorio con mucho trabajo en el hilo principal.
- Una arquitectura web separa interfaz, reglas de negocio y acceso a datos.
- React o Vue permiten tablas, filtros y formularios mas fluidos.
- FastAPI facilita APIs limpias, documentadas y escalables.
- PostgreSQL resuelve mejor concurrencia, integridad e historial que SQLite cuando el sistema crezca.

## Modulos Que Debe Tener La Nueva Version

1. Autenticacion y usuarios
2. Clientes
3. Proyectos
4. Proveedores
5. Inventario de materiales
6. Movimientos de inventario
7. Pedidos de material
8. Herramientas
9. Historial de herramientas
10. Reportes y exportaciones
11. Dashboard

## Fases Recomendadas

### Fase 0: Descubrimiento y congelacion funcional

Objetivo: dejar claro que hace hoy el sistema y que debe migrarse.

Entregables:

- inventario de modulos actuales
- lista de reglas de negocio criticas
- lista de bugs conocidos
- definicion de MVP web

### Fase 1: Base tecnica del nuevo proyecto

Objetivo: crear el esqueleto limpio del sistema web.

Entregables:

- monorepo o estructura `backend/` + `frontend/`
- configuracion de entorno
- autenticacion inicial
- conexion SQLAlchemy
- Alembic
- esquema base de usuarios y auditoria

### Fase 2: Modelo de datos nuevo

Objetivo: reconstruir el dominio con una base de datos mas limpia.

Tablas base sugeridas:

- usuarios
- clientes
- proyectos
- proveedores
- materiales
- movimientos_inventario
- detalles_movimiento
- pedidos_compra
- detalles_pedido
- trabajadores
- herramientas
- asignaciones_herramienta
- historial_herramienta

Entregables:

- modelos SQLAlchemy
- migraciones Alembic
- diagrama entidad relacion

### Fase 3: Inventario y movimientos

Objetivo: migrar el nucleo del negocio primero.

Incluye:

- CRUD de materiales
- busquedas optimizadas
- entradas
- salidas
- devoluciones
- validaciones de stock
- historial de cambios

### Fase 4: Pedidos de material

Objetivo: reemplazar la vista actual de pedidos con una UX moderna y rapida.

Incluye:

- busqueda con debounce
- seleccion de materiales sin bloquear UI
- materiales externos
- guardar materiales nuevos
- vista previa del pedido
- generacion de PDF

### Fase 5: Herramientas e historial

Objetivo: construir el modulo mas trazable y mantenible.

Incluye:

- CRUD de herramientas
- asignacion a trabajadores
- devoluciones
- mantenimiento
- historial filtrable por fecha, trabajador y herramienta
- exportacion PDF

### Fase 6: Reportes y dashboard

Objetivo: consolidar visibilidad de operacion.

Incluye:

- indicadores de stock
- movimientos recientes
- herramientas asignadas
- reportes descargables

### Fase 7: Migracion de datos

Objetivo: llevar la informacion del sistema actual al nuevo.

Incluye:

- script de exportacion del SQLite actual
- transformacion de datos
- importacion al nuevo esquema
- validacion cruzada

### Fase 8: Despliegue

Opciones:

- local simple
- red interna con Docker
- servidor VPS

Entregables:

- `docker-compose.yml`
- variables `.env`
- backup de base de datos
- guia de despliegue

## Orden De Implementacion Recomendado

1. Backend base
2. Modelo de datos
3. Auth
4. Inventario
5. Movimientos
6. Pedidos
7. Herramientas
8. Reportes
9. Migracion de datos
10. Despliegue

## Decision Recomendada De Frontend

### Si quieres mas ecosistema y contratabilidad

Usa `React + TypeScript`

### Si quieres una curva un poco mas amable

Usa `Vue 3 + TypeScript`

## Recomendacion Final

Para este proyecto yo elegiria:

- `FastAPI`
- `SQLAlchemy`
- `Alembic`
- `PostgreSQL`
- `React + TypeScript + Vite`

Eso te da un sistema moderno, mantenible, mas rapido en experiencia de usuario y mejor preparado para crecer.
