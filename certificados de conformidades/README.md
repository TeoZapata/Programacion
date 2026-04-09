# Sistema de Gestión de Certificados RETIE

Sistema empresarial interno para la gestión de certificados de conformidad RETIE, con backend en FastAPI, base de datos PostgreSQL/SQLite, OCR inteligente para extracción de datos desde PDF y panel administrativo web.

## 1. Requisitos previos

- Python 3.10+
- PostgreSQL (para producción) o SQLite (modo local por defecto)
- Tesseract OCR instalado en el sistema
- Poppler instalado (para `pdf2image`)

### Windows – Instalación de dependencias del sistema

1. **Chocolatey (opcional pero recomendado)**  
   Ejecutar en PowerShell (como administrador):

   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; `
   [System.Net.ServicePointManager]::SecurityProtocol = `
   [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; `
   iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. **Instalar Tesseract y Poppler**

   ```powershell
   choco install -y tesseract
   choco install -y poppler
   ```

   Anotar las rutas de instalación para configurarlas en las variables de entorno si es necesario.

## 2. Estructura del proyecto

```text
certificados_retie/
  backend/
    app.py
    config.py
    database.py
    deps.py
    models/
      __init__.py
      user.py
      certificado.py
      certificado_historial.py
    schemas/
      __init__.py
      auth.py
      user.py
      certificado.py
      dashboard.py
    routes/
      auth_routes.py
      user_routes.py
      certificado_routes.py
      dashboard_routes.py
      report_routes.py
    services/
      ocr_service.py
      pdf_service.py
      certificate_service.py
      alert_service.py
      backup_service.py
    utils/
      security.py
      validators.py
  frontend/
    templates/
      base.html
      login.html
      dashboard.html
      certificados.html
      certificado_form.html
      buscar.html
      reportes.html
      usuarios.html
    static/
      css/
        styles.css
      js/
        main.js
        dashboard.js
        certificados.js
  uploads/
    pdf/
    images/
  tests/
    test_auth.py
    test_certificados.py
  requirements.txt
  README.md
```

## 3. Configuración del entorno

Desde la carpeta raíz del proyecto:

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

Crear un archivo `.env` en la raíz o en `backend/` con contenido similar:

```env
ENVIRONMENT=development
SECRET_KEY=super_secret_key_cambiala
ACCESS_TOKEN_EXPIRE_MINUTES=60
ALGORITHM=HS256

DATABASE_URL_SQLITE=sqlite:///./certificados_retie.db
DATABASE_URL_POSTGRESQL=postgresql+psycopg2://user:password@localhost:5432/certificados_retie

USE_SQLITE=1

UPLOAD_DIR=uploads
PDF_UPLOAD_DIR=uploads/pdf
IMAGE_UPLOAD_DIR=uploads/images

TESSERACT_CMD=C:\\Program Files\\Tesseract-OCR\\tesseract.exe
POPPLER_PATH=C:\\Program Files\\poppler-24.02.0\\Library\\bin

LLM_API_URL=https://mi-llm-empresarial.local/api/v1/parse
LLM_API_KEY=CAMBIAR_POR_API_KEY
```

## 4. Inicializar base de datos

```powershell
.venv\Scripts\activate
python -m backend.database
```

Ese comando creará las tablas necesarias en la base de datos seleccionada.

## 5. Ejecutar el servidor en red local

Desde la raíz del proyecto:

```powershell
.venv\Scripts\activate
uvicorn backend.app:app --host 0.0.0.0 --port 5000 --reload
```

Acceder desde otros equipos de la red local usando la IP del servidor:

```text
http://192.168.1.100:5000
```

## 6. Usuario administrador inicial

Tras la primera ejecución, crear un usuario administrador mediante una llamada a la API o un script de inicialización (incluido en el backend). Ver detalles en la sección de autenticación de este README (pendiente de ampliar).

## 7. Pruebas automatizadas

Ejecutar tests:

```powershell
.venv\Scripts\activate
pytest
```

## 8. Despliegue en producción

- Usar PostgreSQL y configurar `USE_SQLITE=0`.
- Ejecutar `uvicorn` detrás de un servidor inverso (Nginx/Apache) o usar un servicio como systemd en Linux.
- Configurar copias de seguridad automáticas usando el script de backup incluido y el programador de tareas del sistema.

