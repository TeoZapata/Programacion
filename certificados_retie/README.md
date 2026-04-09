# ⚡ Sistema de Gestión de Certificados RETIE

**Software empresarial para gestión documental de certificados de conformidad RETIE**

> Desarrollado para empresas instaladoras de sistemas eléctricos y fotovoltaicos en Colombia.
> Cumple con los requerimientos del Reglamento Técnico de Instalaciones Eléctricas (RETIE).

---

## 🎯 ¿Qué hace este sistema?

| Funcionalidad | Descripción |
|---|---|
| 📋 **Registro de certificados** | Formulario completo con todos los campos RETIE |
| 🤖 **OCR Automático** | Extrae datos del PDF automáticamente |
| 📅 **Control de vencimientos** | Alertas a 30, 60 y 90 días |
| 🔍 **Búsqueda avanzada** | Filtros por producto, organismo, estado, fechas |
| 📊 **Dashboard** | Gráficas interactivas con Chart.js |
| 📥 **Exportación Excel** | Reportes completos y de vencimientos |
| 👥 **Multi-usuario** | Roles ADMIN y USUARIO |
| 🔐 **Seguridad** | Autenticación JWT, hashes de contraseñas |

---

## 🏗️ Arquitectura

```
certificados_retie/
├── app.py                          # Punto de entrada Flask
├── .env                            # Variables de entorno
├── requirements.txt                # Dependencias Python
│
├── backend/
│   ├── config.py                   # Configuraciones por entorno
│   ├── database.py                 # SQLAlchemy + seed inicial
│   ├── models/
│   │   ├── user.py                 # Modelo Usuario (Flask-Login)
│   │   └── certificado.py          # Modelo Certificado (estados, OCR)
│   ├── routes/
│   │   ├── auth_routes.py          # Login/logout/usuarios
│   │   ├── certificado_routes.py   # CRUD certificados + PDF
│   │   ├── dashboard_routes.py     # Dashboard + API stats
│   │   └── report_routes.py        # Exportación Excel
│   ├── services/
│   │   ├── ocr_service.py          # OCR: PDF→imagen→texto→campos
│   │   ├── certificate_service.py  # Lógica de negocio certificados
│   │   └── report_service.py       # Generación de reportes Excel
│   └── utils/
│       └── validators.py           # Validaciones y seguridad
│
├── frontend/
│   ├── templates/
│   │   ├── base.html               # Layout con sidebar
│   │   ├── login.html              # Página de inicio de sesión
│   │   ├── dashboard.html          # Panel principal con gráficas
│   │   ├── certificados.html       # Lista con búsqueda
│   │   ├── crear_certificado.html  # Formulario + carga PDF
│   │   ├── detalle_certificado.html # Vista completa + visor PDF
│   │   ├── editar_certificado.html # Edición de datos
│   │   ├── usuarios.html           # Gestión de usuarios (ADMIN)
│   │   └── nuevo_usuario.html      # Crear usuario
│   └── static/
│       ├── css/                    # Estilos adicionales
│       └── js/                     # Scripts adicionales
│
├── uploads/
│   ├── pdf/                        # PDFs de certificados
│   └── images/                     # Imágenes OCR
│
└── tests/
    └── test_sistema_retie.py       # Tests unitarios y de API
```

---

## 🚀 Instalación Rápida

### Linux / Ubuntu (Recomendado)

```bash
# 1. Clonar o descomprimir el proyecto
cd certificados_retie/

# 2. Dar permisos y ejecutar instalador
chmod +x instalar.sh
./instalar.sh

# 3. Iniciar el sistema
source venv/bin/activate
python app.py
```

### Windows

```batch
# Doble clic en:
instalar_windows.bat

# Luego iniciar:
iniciar.bat
```

### Manual (cualquier sistema)

```bash
# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate   # Linux
# venv\Scripts\activate.bat  # Windows

# Instalar dependencias
pip install -r requirements.txt

# Instalar Tesseract OCR (Ubuntu)
sudo apt install tesseract-ocr tesseract-ocr-spa poppler-utils

# Crear carpetas de uploads
mkdir -p uploads/pdf uploads/images

# Iniciar
python app.py
```

---

## 🌐 Acceso desde la Red Local

1. Obtener la IP del servidor:
   ```bash
   ip addr show  # Linux
   ipconfig      # Windows
   ```

2. Acceder desde cualquier computador de la red:
   ```
   http://192.168.1.XXX:5000
   ```

3. Credenciales iniciales:
   - **Usuario:** `admin`
   - **Contraseña:** `admin123`
   - ⚠️ Cambiar inmediatamente después del primer acceso

---

## 🗄️ Base de Datos

### Modo desarrollo (SQLite)

Archivo local `retie_dev.db`. No requiere configuración adicional.

### Modo producción (PostgreSQL)

```sql
-- Crear base de datos PostgreSQL
CREATE DATABASE retie_db;
CREATE USER retie_user WITH PASSWORD 'retie_pass_seguro';
GRANT ALL PRIVILEGES ON DATABASE retie_db TO retie_user;
```

Actualizar en `.env`:
```env
DATABASE_URL=postgresql://retie_user:retie_pass_seguro@localhost:5432/retie_db
```

### Tablas creadas automáticamente

**`usuarios`**
| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER PK | Autoincremental |
| nombre | VARCHAR(120) | Nombre completo |
| correo | VARCHAR(180) UNIQUE | Correo electrónico |
| usuario | VARCHAR(50) UNIQUE | Nombre de usuario |
| password_hash | VARCHAR(256) | Hash bcrypt |
| rol | VARCHAR(20) | ADMIN / USUARIO |
| activo | BOOLEAN | Estado de la cuenta |
| ultimo_login | DATETIME | Último acceso |

**`certificados`**
| Campo | Tipo | Descripción |
|---|---|---|
| id | INTEGER PK | Autoincremental |
| numero_certificado | VARCHAR(100) UNIQUE | N° del certificado |
| convenio | VARCHAR(200) | Convenio/marca |
| producto | VARCHAR(200) | Nombre del producto |
| descripcion | TEXT | Descripción técnica |
| organismo_certificador | VARCHAR(200) | Entidad certificadora |
| fecha_emision | DATE | Fecha de emisión |
| fecha_vencimiento | DATE | Fecha de vencimiento |
| fecha_registro | DATETIME | Registro en el sistema |
| archivo_pdf | VARCHAR(300) | Nombre del archivo PDF |
| imagen_extraida | VARCHAR(300) | Imagen OCR |
| estado_certificado | VARCHAR(20) | vigente/por_vencer/vencido |
| texto_ocr | TEXT | Texto extraído por OCR |
| confianza_ocr | FLOAT | Confianza del OCR (0-1) |

---

## 🤖 OCR Automático

El sistema incluye un pipeline de extracción de información:

```
PDF → PyMuPDF (imagen) → OpenCV (limpieza) → Tesseract → Regex → Datos
```

**Datos detectados automáticamente:**
- ✅ Número de certificado
- ✅ Organismo certificador (ICONTEC, SGS, Bureau Veritas, etc.)
- ✅ Nombre del producto
- ✅ Fecha de emisión
- ✅ Fecha de vencimiento

Si el OCR no detecta algún campo, el usuario puede completarlo manualmente.

**Requisitos del OCR:**
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr tesseract-ocr-spa poppler-utils libgl1-mesa-glx

# Verificar instalación
tesseract --version
```

---

## 📊 Estados de Certificados

| Estado | Condición | Color |
|---|---|---|
| ✅ **Vigente** | Vence en > 30 días | Verde |
| ⚠️ **Por Vencer** | Vence en ≤ 30 días | Amarillo/Naranja |
| ❌ **Vencido** | Ya venció | Rojo |

Los estados se actualizan automáticamente en cada visita al sistema.

---

## 🔒 Seguridad

- Contraseñas hasheadas con **Werkzeug** (bcrypt-compatible)
- Autenticación por sesión con **Flask-Login**
- Control de acceso por **rol** (ADMIN / USUARIO)
- Validación de extensión y contenido de archivos PDF
- Protección CSRF en formularios
- Nombres de archivo sanitizados con `secure_filename`

---

## 🧪 Ejecutar Tests

```bash
# Activar entorno virtual
source venv/bin/activate

# Ejecutar todos los tests
pytest tests/ -v

# Con reporte de cobertura
pip install pytest-cov
pytest tests/ -v --cov=backend --cov-report=html
```

---

## 📦 Dependencias Principales

| Librería | Versión | Uso |
|---|---|---|
| Flask | 3.0.0 | Framework web |
| Flask-SQLAlchemy | 3.1.1 | ORM base de datos |
| Flask-Login | 0.6.3 | Autenticación |
| PyMuPDF | 1.23.7 | Renderizado PDF |
| pytesseract | 0.3.10 | OCR |
| opencv-python-headless | 4.8.1 | Procesamiento imagen |
| pdfplumber | 0.10.3 | Extracción texto PDF |
| openpyxl | 3.1.2 | Exportación Excel |
| Chart.js | 4.4.0 | Gráficas (CDN) |
| Bootstrap | 5.3.2 | UI (CDN) |

---

## 🔧 Variables de Entorno (.env)

```env
FLASK_ENV=development          # development | production
FLASK_DEBUG=false
SECRET_KEY=clave-secreta-larga-y-unica
HOST=0.0.0.0                   # 0.0.0.0 para red local
PORT=5000

# SQLite (desarrollo)
DATABASE_URL=sqlite:///retie_dev.db

# PostgreSQL (producción)
# DATABASE_URL=postgresql://user:pass@localhost:5432/retie_db

# Ruta a Tesseract OCR
TESSERACT_CMD=/usr/bin/tesseract
# Windows: TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

---

## 📈 Escalabilidad

El sistema está diseñado para evolucionar:

- **Base de datos:** Migración SQLite → PostgreSQL con solo cambiar `DATABASE_URL`
- **Servidor web:** Reemplazar `python app.py` por **Gunicorn + Nginx**
- **Nube:** Compatible con cualquier VPS (DigitalOcean, AWS, Google Cloud)
- **Docker:** Agregar `Dockerfile` y `docker-compose.yml` cuando sea necesario

### Producción con Gunicorn

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"
```

---

## 📞 Soporte

Para problemas con la instalación o uso del sistema, verificar:

1. ✅ Python 3.9+ instalado
2. ✅ `tesseract-ocr` instalado para OCR
3. ✅ `poppler-utils` instalado para conversión PDF
4. ✅ Carpetas `uploads/pdf` y `uploads/images` existen
5. ✅ Archivo `.env` configurado

---

*Sistema RETIE — Gestión de Certificados de Conformidad Eléctrica*
*Compatible con RETIE - Resolución 90708 de 2013 y sus actualizaciones*
