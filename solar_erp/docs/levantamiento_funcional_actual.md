# Levantamiento Funcional Actual: GeoInventario

## Proposito

Este documento describe el comportamiento actual del sistema GeoInventario para servir como base de migracion a la nueva version web.

No busca documentar cada linea del codigo, sino responder:

- que modulos existen hoy
- que hace cada modulo
- que datos maneja
- que reglas de negocio son visibles
- que problemas y mejoras deben considerarse al migrar

## Vision General Del Sistema Actual

GeoInventario es una aplicacion de escritorio en Python con interfaz PySide/Qt y base de datos SQLite.

Actualmente funciona como una herramienta operativa para:

- gestionar proyectos
- controlar inventario de materiales
- registrar entradas, salidas y devoluciones
- generar pedidos de material
- administrar herramientas y sus asignaciones
- manejar usuarios, clientes, proveedores y trabajadores
- emitir reportes y documentos PDF o Word

## Arquitectura Actual

El proyecto tiene una separacion parcial en capas:

- `models`: estructura de datos
- `repositories`: acceso a base de datos
- `services`: logica de negocio
- `ui`: vistas Qt
- `reports`: generacion de documentos
- `utils`: utilidades transversales

Observacion importante:

Aunque existe esa separacion, varias vistas todavia abren sesiones de base de datos y ejecutan logica directamente desde la UI. La nueva version web debe corregir esto.

## Navegacion Principal Actual

Segun [main_window.py](D:/Users/Mateo/Documents/GitHub/Programacion/solar_erp/app/ui/main_window.py), el sistema actual contiene estos modulos visibles:

1. Dashboard
2. Proyectos
3. Clientes
4. Proveedores
5. Trabajadores
6. Inventario
7. Movimientos
8. Herramientas
9. Pedido de Material
10. Control Proyecto
11. Usuarios

El modulo de usuarios aparece solo para rol administrador.

## Roles Y Acceso

Existen roles de usuario definidos en el sistema:

- administrador
- tecnico
- inventario

En la version actual el rol se usa principalmente para visibilidad/acceso desde la interfaz. En la migracion web debe formalizarse con permisos por endpoint y por modulo.

## Modulos Funcionales Actuales

### 1. Autenticacion Y Usuarios

Responsabilidad actual:

- login al sistema
- administracion de usuarios
- asignacion de rol
- activacion o desactivacion

Comportamiento observado:

- el login valida usuario activo y contrasena
- el sistema migra automaticamente hashes viejos cuando el usuario inicia sesion
- existe modulo de administracion de usuarios para crear, editar y eliminar

Reglas visibles:

- un usuario inactivo no debe autenticarse
- las contrasenas nuevas usan hash reforzado

Migracion recomendada:

- autenticacion centralizada en backend
- permisos por rol y por accion
- sesiones seguras

### 2. Clientes

Responsabilidad actual:

- CRUD de clientes

Datos visibles:

- nombre
- identificacion
- telefono
- email
- direccion
- observaciones

Relacion de negocio:

- un cliente puede tener multiples proyectos

Migracion recomendada:

- tabla simple con formularios y busqueda
- integracion directa con proyectos

### 3. Proveedores

Responsabilidad actual:

- CRUD de proveedores

Datos visibles:

- nombre
- NIT
- telefono
- email
- direccion

Relacion de negocio:

- un material puede asociarse a proveedor
- las entradas de inventario pueden estar vinculadas a proveedor y factura

### 4. Trabajadores

Responsabilidad actual:

- CRUD de trabajadores

Datos visibles:

- nombre
- cargo
- telefono
- estado

Relacion de negocio:

- se usan para asignar herramientas
- deben poder filtrar historial de herramientas

### 5. Proyectos

Responsabilidad actual:

- CRUD de proyectos solares
- asociacion con cliente
- datos tecnicos del proyecto

Datos visibles en el modelo actual:

- nombre del proyecto
- cliente
- direccion
- fecha de inicio
- estado
- cantidad de paneles
- potencia por panel
- potencia total DC calculada
- potencia total AC
- modelo de inversor
- cantidad de inversores

Reglas visibles:

- `potencia_total_dc = (cantidad_paneles * potencia_panel) / 1000`
- los proyectos se usan como destino para salidas de inventario
- existen vistas adicionales asociadas a control y costos de proyecto

Migracion recomendada:

- separar datos comerciales de datos tecnicos
- mantener trazabilidad de consumo de materiales por proyecto

### 6. Inventario De Materiales

Responsabilidad actual:

- CRUD de materiales
- alertas de stock bajo
- valorizacion de inventario

Datos visibles:

- nombre_material
- categoria
- unidad
- cantidad_actual
- stock_minimo
- precio_unitario
- ubicacion
- proveedor_id

Reglas visibles:

- se detecta stock bajo cuando `cantidad_actual <= stock_minimo`
- existe fusion opcional por nombre al crear/importar materiales
- el valor total del inventario puede calcularse con `precio_unitario * cantidad_actual`

Problemas detectados:

- la UI del escritorio sufre cuando hay muchos registros
- parte de la experiencia de busqueda y tabla se vuelve pesada

Migracion recomendada:

- tabla paginada
- filtros por nombre, categoria, ubicacion y stock bajo
- backend con busqueda y frontend con debounce

### 7. Movimientos De Inventario

Responsabilidad actual:

- registrar entradas
- registrar salidas
- registrar devoluciones
- afectar stock automaticamente
- asociar consumo a proyecto

Tipos actuales:

- `entrada`
- `salida`
- `devolucion`

Datos visibles por movimiento:

- proveedor o proyecto segun tipo
- fecha
- responsable
- observaciones
- detalle de materiales y cantidades

Reglas visibles:

- una entrada suma stock
- una salida descuenta stock
- una devolucion vuelve a sumar stock
- una salida no puede exceder stock disponible
- en entradas puede registrarse precio unitario
- en salidas y devoluciones se guarda trazabilidad financiera por proyecto usando `SalidaProyecto`

Valor para la migracion:

- este modulo es uno de los nucleos del sistema
- debe migrarse antes que reportes complejos

### 8. Pedido De Material

Responsabilidad actual:

- construir una solicitud de materiales desde inventario
- detectar si hay materiales disponibles o faltantes
- permitir agregar materiales no existentes
- generar reporte PDF
- registrar pedido en base de datos

Flujo actual:

1. usuario busca materiales
2. define cantidades requeridas
3. el sistema compara contra stock actual
4. separa materiales en:
   - disponibles
   - a comprar
5. permite agregar material externo si no existe en inventario
6. puede guardar ese material nuevo en inventario con stock cero
7. genera PDF del pedido
8. registra pedido en base de datos

Reglas visibles:

- si el material existe y alcanza, queda como disponible
- si no alcanza, se calcula faltante
- si no existe, puede agregarse como externo
- si se guarda en inventario desde el dialogo, queda con stock inicial cero

Problemas observados:

- la UI de pedidos es sensible a la cantidad de controles en tabla
- la experiencia se resiente con listas grandes

Migracion recomendada:

- selector de materiales con busqueda asincrona
- carrito de pedido fuera de la grilla principal
- tabla de pedido separada de la tabla maestra

### 9. Herramientas

Responsabilidad actual:

- inventario de herramientas
- asignacion a trabajadores
- devolucion de herramientas
- mantenimiento
- historial de herramientas
- reportes

Datos visibles de herramienta:

- codigo
- nombre
- categoria
- marca
- modelo
- numero de serie
- estado
- ubicacion
- observaciones

Estados visibles:

- disponible
- asignada
- mantenimiento
- baja

Flujo actual:

1. crear o editar herramienta
2. asignar a trabajador
3. devolver
4. cambiar estado
5. consultar historial
6. exportar reportes

Reglas visibles:

- una herramienta asignada no debe volver a asignarse sin devolucion
- al asignar, cambia a estado `asignada`
- al devolver, cambia a `disponible`
- existe historial persistente para:
  - creacion
  - asignacion
  - devolucion
  - mantenimiento
  - cambio de estado

Filtros actuales del historial:

- fecha desde
- fecha hasta
- trabajador
- texto libre

Reportes actuales:

- reporte general
- reporte por trabajador
- reporte PDF del historial

### 10. Dashboard

Responsabilidad actual:

- mostrar resumen operativo
- accesos rapidos
- indicadores

Indicadores esperables segun el sistema:

- proyectos activos
- materiales con stock bajo
- movimientos recientes
- herramientas asignadas o en mantenimiento

Migracion recomendada:

- construirlo despues de inventario y movimientos
- consumir KPIs ya calculados por backend

### 11. Control Proyecto Y Costos

Estos modulos aparecen en la estructura actual, aunque no fueron analizados en detalle en esta fase.

Lo que puede inferirse con seguridad:

- existe un seguimiento de salidas o costos por proyecto
- el modelo `SalidaProyecto` respalda trazabilidad financiera y de consumo

Recomendacion para migracion:

- documentarlos mas a fondo antes de implementarlos
- probablemente deben ir despues de inventario, movimientos y proyectos

## Reportes Y Documentos Actuales

El sistema actual genera archivos PDF y Word.

Casos confirmados:

- pedido de material en PDF
- reportes de herramientas
- reportes de historial de herramientas
- documentos operativos de movimientos o actas

Problema arquitectonico actual:

- parte de la logica documental esta repartida entre vistas y funciones de reporte

Migracion recomendada:

- toda generacion documental debe quedar en backend
- el frontend solo dispara la accion y descarga el archivo

## Modelo De Datos Actual Confirmado

Tablas y entidades principales confirmadas:

- usuarios
- clientes
- proveedores
- trabajadores
- proyectos
- materiales
- movimientos_inventario
- detalles_movimiento
- pedidos_compra
- detalles_pedido
- herramientas
- asignaciones_herramienta
- historial_herramientas
- salidas_proyecto

## Reglas De Negocio Criticas A Preservar

1. No permitir salidas de inventario sin stock suficiente.
2. Mantener calculo de faltantes en pedidos.
3. Conservar trazabilidad entre proyecto y consumo de materiales.
4. Registrar historial de herramientas en cada evento importante.
5. Mantener distincion entre materiales en stock y materiales a comprar.
6. Mantener control por rol de usuario.

## Problemas Funcionales Y Tecnicos Detectados

1. La UI de escritorio se bloquea con tablas grandes o widgets pesados.
2. Existe logica de negocio demasiado cerca de la vista.
3. Hay archivos de UI muy grandes y con muchas responsabilidades.
4. Algunas busquedas o refrescos no escalan bien.
5. La documentacion historica no coincide del todo con el codigo actual.

## Que Debe Hacer La Nueva Version Web

La nueva version no debe ser una copia literal de la UI actual.

Debe conservar:

- reglas de negocio
- entidades
- historial
- trazabilidad
- reportes clave

Debe mejorar:

- experiencia de busqueda
- rendimiento de listas
- separacion de capas
- soporte multiusuario
- despliegue

## Orden Recomendado De Documentacion Detallada Antes De Reescribir

1. Inventario
2. Movimientos
3. Pedidos
4. Herramientas
5. Historial de herramientas
6. Usuarios y permisos
7. Proyectos
8. Dashboard
9. Control de proyecto y costos

## Uso De Este Documento

La siguiente ventana de Codex debe usar este archivo para:

- entender el producto actual
- priorizar el MVP web
- saber que reglas no puede perder
- planear la migracion modulo por modulo
