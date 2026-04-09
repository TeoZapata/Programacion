# ⚡ RETIE Manager

**Sistema de Gestión de Proyectos Eléctricos y Fotovoltaicos bajo Normativa RETIE — Colombia**

---

## 📋 Descripción

RETIE Manager es una aplicación de escritorio profesional desarrollada en Python con interfaz PySide6 (Qt), base de datos SQLite y generación automática de documentos Word. Diseñada para ingenieros eléctricos colombianos que necesitan gestionar proyectos bajo la normativa RETIE (Resolución 90708 de 2013).

---

## 🖥️ Requisitos del Sistema

- **Python:** 3.9 o superior
- **Sistema operativo:** Windows 10/11, Linux (Ubuntu 20+), macOS 12+
- **RAM:** 4 GB mínimo
- **Disco:** 500 MB libres

---

## ⚙️ Instalación

### Instalación rápida (recomendada)

```bash
# Clonar o descomprimir el proyecto
cd retie_app

# Ejecutar el instalador automático
python instalar.py
```

### Instalación manual

```bash
pip install PySide6 python-docx
python main.py
```

---

## 🚀 Inicio de Sesión

Al iniciar por primera vez, use las credenciales por defecto:

| Campo | Valor |
|-------|-------|
| **Usuario** | `admin` |
| **Contraseña** | `admin123` |

> ⚠️ Cambie la contraseña en **Configuración** después del primer inicio de sesión.

---

## 📁 Estructura del Proyecto

```
retie_app/
├── main.py                   # Punto de entrada
├── instalar.py               # Instalador automático
├── requirements.txt          # Dependencias
├── core/
│   └── database.py           # Modelos, BD SQLite, DAOs
├── modules/
│   ├── dimensionamiento.py   # Cálculos fotovoltaicos
│   └── generador_docs.py     # Motor de documentos Word
├── ui/
│   ├── styles.py             # Temas y estilos QSS
│   ├── widgets.py            # Componentes reutilizables
│   ├── login.py              # Ventana de login
│   ├── panels.py             # Todos los paneles principales
│   └── main_window.py        # Ventana principal con sidebar
└── README.md
```

---

## 📌 Módulos del Sistema

### 1. 🔐 Autenticación
- Login seguro con contraseñas hasheadas (SHA-256)
- Roles: **Administrador** e **Ingeniero**
- Gestión de usuarios (solo administrador)

### 2. ⚙️ Configuración del Ingeniero
Datos del profesional que se insertan automáticamente en todos los documentos:
- Nombre, cédula, matrícula profesional
- Empresa, NIT, dirección, teléfono, correo

### 3. 👥 Gestión de Clientes
- Registro completo con búsqueda en tiempo real
- Nombre, cédula/NIT, dirección, teléfono, correo

### 4. 📁 Gestión de Proyectos
- Proyectos eléctricos y fotovoltaicos
- Datos de ubicación por departamento colombiano
- Seguimiento de estados: activo, en proceso, finalizado, pausado

### 5. ☀️ Sistema Fotovoltaico
Por cada proyecto de tipo FV se registran:
- **Paneles:** cantidad, potencia, marca, referencia
- **Inversores:** cantidad, marca, referencia, potencia
- **Eléctricos:** calibre, tipo de conductor, breaker

### 6. 🔢 Dimensionamiento Solar Automático
Calcula según datos reales de Colombia:
- Potencia pico requerida del sistema (kWp)
- Número de paneles necesarios
- Generación estimada mensual (kWh/mes)
- Área aproximada requerida (m²)
- Basado en radiación solar por departamento colombiano

### 7. 🖼️ Gestión de Imágenes
Imágenes técnicas por proyecto:
- Ubicación del proyecto
- Cuadro de cargas
- Caída de tensión
- Regulación y pérdidas
- Diagrama unifilar

### 8. 📋 Plantillas Word
- Cargue sus propias plantillas `.docx`
- Variables tipo `{{cliente_nombre}}` reemplazadas automáticamente
- Incluye botón para crear plantillas de ejemplo

### 9. 📄 Generación de Documentos
Documentos pre-configurados:
- Acta de inicio de obra
- Declaración de construcción RETIE
- Declaración de diseño RETIE
- Memoria de cálculo
- (Cargar plantillas personalizadas adicionales)

### 10. 📂 Carpeta del Proyecto
Al generar documentos se crea automáticamente:
```
~/RETIE_Manager/Proyectos/NOMBRE_PROYECTO/
├── documentos/        # Documentos .docx generados
├── imagenes/          # Imágenes del proyecto
├── plantillas/        # Plantillas copiadas
└── datos_proyecto.json
```

---

## 🌐 Uso en Red Local

Para compartir la base de datos entre múltiples equipos:

1. **Copie** `retie.db` a una carpeta compartida de red
2. En cada equipo, configure la ruta en **Configuración → Ruta de BD**:
   - Windows: `\\servidor\compartida\retie.db`
   - Linux: `/mnt/servidor/retie.db`
3. **Reinicie** la aplicación en cada equipo

La base de datos SQLite usa `WAL mode` para soportar múltiples lecturas concurrentes.

---

## 📝 Variables Disponibles para Plantillas

Use estas variables en sus plantillas `.docx` con el formato `{{variable}}`:

| Variable | Descripción |
|----------|-------------|
| `{{fecha_actual}}` | Fecha completa en español |
| `{{ingeniero_nombre}}` | Nombre del ingeniero |
| `{{ingeniero_matricula}}` | Matrícula profesional |
| `{{empresa_nombre}}` | Nombre de la empresa |
| `{{empresa_nit}}` | NIT de la empresa |
| `{{cliente_nombre}}` | Nombre del cliente |
| `{{cliente_cedula_nit}}` | Cédula o NIT del cliente |
| `{{nombre_proyecto}}` | Nombre del proyecto |
| `{{proyecto_ciudad}}` | Ciudad del proyecto |
| `{{proyecto_departamento}}` | Departamento del proyecto |
| `{{cantidad_paneles}}` | Número de paneles FV |
| `{{potencia_panel}}` | Potencia del panel (Wp) |
| `{{marca_panel}}` | Marca de los paneles |
| `{{marca_inversor}}` | Marca de los inversores |
| `{{potencia_total_kwp}}` | Potencia total del sistema |
| `{{generacion_estimada_kwh}}` | Generación estimada mensual |
| *(y muchas más...)* | Ver panel de Plantillas |

---

## ⚡ Normativa Aplicada

- **RETIE:** Resolución 90708 de 2013 y modificaciones
- **NTC 2050:** Código Eléctrico Colombiano
- **IEC 62446:** Sistemas fotovoltaicos — Requisitos para pruebas
- **CREG 030 de 2018:** Generación distribuida conectada a la red

---

## 🛠️ Tecnologías

| Tecnología | Uso |
|------------|-----|
| Python 3.9+ | Lenguaje principal |
| PySide6 (Qt 6) | Interfaz gráfica |
| SQLite3 | Base de datos |
| python-docx | Generación de documentos Word |

---

## 📞 Soporte

Para reportar errores o solicitar funcionalidades, revise el código fuente en `core/database.py`, `modules/` y `ui/panels.py`.

---

*RETIE Manager v1.0.0 — Desarrollado para ingenieros eléctricos colombianos*
