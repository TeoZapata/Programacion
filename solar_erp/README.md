# ☀ Solar ERP — Sistema de Gestión Solar Fotovoltaico

Aplicación de escritorio completa para gestionar inventario, proyectos y operaciones
de una empresa instaladora de sistemas solares fotovoltaicos.

---

## 🚀 Instalación y Ejecución

### 1. Requisitos previos
- Python 3.11 o superior
- pip

### 2. Crear entorno virtual (recomendado)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Ejecutar la aplicación
```bash
python app/main.py
```

---

## 🔐 Acceso inicial

| Usuario | Contraseña | Rol            |
|---------|------------|----------------|
| admin   | admin123   | Administrador  |

> **Cambia la contraseña después del primer acceso** desde el módulo de Usuarios.

---

## 📂 Estructura del Proyecto

```
solar_erp/
├── app/
│   ├── main.py                  # Punto de entrada
│   ├── core/
│   │   ├── config.py            # Configuración global
│   │   └── database.py          # SQLAlchemy + SQLite
│   ├── models/                  # Modelos de la base de datos
│   │   ├── usuario.py
│   │   ├── cliente.py
│   │   ├── proveedor.py
│   │   ├── trabajador.py
│   │   ├── proyecto.py
│   │   ├── inventario.py
│   │   └── movimiento.py
│   ├── repositories/            # Acceso a datos
│   │   └── repositories.py
│   ├── services/                # Lógica de negocio
│   │   └── services.py
│   ├── ui/                      # Interfaz gráfica PySide6
│   │   ├── main_window.py       # Ventana principal + sidebar
│   │   ├── login.py             # Pantalla de login
│   │   ├── dashboard.py         # Panel principal
│   │   ├── clientes_view.py
│   │   ├── proveedores_view.py
│   │   ├── trabajadores_view.py
│   │   ├── proyectos_view.py
│   │   ├── inventario_view.py
│   │   ├── movimientos_view.py
│   │   ├── usuarios_view.py
│   │   ├── base_view.py         # Vista CRUD reutilizable
│   │   └── styles.py            # Stylesheet global
│   ├── reports/
│   │   └── acta_materiales.py   # Generador de documentos Word
│   └── utils/
│       └── security.py          # Hash de contraseñas
├── database/
│   └── solar_erp.db             # Base de datos SQLite (se crea automáticamente)
├── documentos/                  # Actas Word generadas
├── requirements.txt
└── README.md
```

---

## 🗄️ Base de Datos

La base de datos SQLite se crea automáticamente en `database/solar_erp.db`
al ejecutar la aplicación por primera vez.

### Tablas principales:
- **usuarios** — Login y roles (administrador, técnico, inventario)
- **clientes** — Datos de clientes
- **proveedores** — Proveedores de materiales
- **trabajadores** — Personal técnico
- **proyectos** — Proyectos solares (con datos técnicos)
- **materiales** — Inventario de materiales y herramientas
- **movimientos** — Entradas, salidas y devoluciones de inventario
- **detalle_movimientos** — Ítems de cada movimiento

---

## ⚡ Funcionalidades principales

### Proyectos Solares
- Gestión completa de proyectos vinculados a clientes
- Cálculo automático de potencia DC: `kWp = (paneles × Wp_panel) / 1000`
- Estados de proyecto: Prospecto → En diseño → Aprobado → En ejecución → Completado

### Inventario
- Registro de materiales con categorías, unidades y ubicación
- Alertas automáticas de stock bajo (resaltado en rojo)
- Dashboard con contadores de alertas en tiempo real

### Movimientos
- **Entrada**: Compra de material a proveedor con precio y factura
- **Salida**: Entrega de materiales a un proyecto (descuenta inventario)
- **Devolución**: Retorno de materiales al inventario
- Actualización automática de cantidades

### Documentos Word
- Generación automática de Acta de Entrega de Materiales (.docx) al registrar salidas
- Incluye: proyecto, cliente, fecha, lista de materiales, responsable y firmas

---

## 🖥️ Multiusuario en Red Local

Para usar en múltiples equipos en red local:

1. Mueve la base de datos `solar_erp.db` a una carpeta compartida en la red
2. Edita `app/core/config.py`:
   ```python
   DATABASE_URL = "sqlite:////ruta/compartida/solar_erp.db"
   ```
3. Instala la aplicación en cada equipo y apunta a la misma ruta de red

> **Nota**: Para alta concurrencia (10+ usuarios simultáneos), considera migrar a PostgreSQL
> cambiando `DATABASE_URL` y agregando `psycopg2` a requirements.txt.

---

## 📦 Empaquetar como ejecutable (opcional)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "SolarERP" app/main.py
```

El ejecutable quedará en `dist/SolarERP.exe`

---

## 🔄 Roles del sistema

| Rol           | Acceso                                           |
|---------------|--------------------------------------------------|
| administrador | Acceso total + gestión de usuarios               |
| tecnico       | Proyectos, clientes, movimientos (solo lectura inventario) |
| inventario    | Inventario y movimientos                         |

---

## 📋 Tecnologías usadas

- **Python 3.11+**
- **PySide6** — Interfaz gráfica Qt
- **SQLAlchemy 2.0** — ORM
- **SQLite** — Base de datos
- **python-docx** — Generación de documentos Word
