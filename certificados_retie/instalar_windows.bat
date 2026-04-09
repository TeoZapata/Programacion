@echo off
REM ==============================================================
REM instalar_windows.bat
REM Instalación del Sistema RETIE en Windows
REM ==============================================================

echo.
echo ====================================================
echo    SISTEMA RETIE - INSTALACION EN WINDOWS
echo ====================================================
echo.

REM Verificar Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python no encontrado.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo IMPORTANTE: Marca la casilla "Add Python to PATH"
    pause
    exit /b 1
)

echo [OK] Python encontrado

REM Crear entorno virtual
if not exist "venv" (
    echo Creando entorno virtual...
    python -m venv venv
    echo [OK] Entorno virtual creado
) else (
    echo [INFO] Entorno virtual ya existe
)

REM Activar entorno virtual
call venv\Scripts\activate.bat

REM Actualizar pip
python -m pip install --upgrade pip

REM Instalar dependencias
echo Instalando dependencias Python...
pip install -r requirements.txt
echo [OK] Dependencias instaladas

REM Crear directorios
if not exist "uploads\pdf" mkdir uploads\pdf
if not exist "uploads\images" mkdir uploads\images
echo [OK] Directorios creados

REM Crear .env
if not exist ".env" (
    echo Creando configuracion...
    (
        echo FLASK_ENV=development
        echo FLASK_DEBUG=false
        echo SECRET_KEY=retie-2024-windows-clave
        echo HOST=0.0.0.0
        echo PORT=5000
        echo DATABASE_URL=sqlite:///retie_dev.db
        echo TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
    ) > .env
    echo [OK] Archivo .env creado
)

REM Inicializar DB
echo Inicializando base de datos...
python -c "from app import create_app; app = create_app(); print('OK')"

echo.
echo ====================================================
echo    INSTALACION COMPLETADA
echo ====================================================
echo.
echo Para iniciar el sistema, ejecuta:
echo    iniciar.bat
echo.
echo O manualmente:
echo    venv\Scripts\activate.bat
echo    python app.py
echo.
echo Acceso: http://localhost:5000
echo Usuario: admin
echo Password: admin123
echo.

REM Crear script de inicio
(
    echo @echo off
    echo call venv\Scripts\activate.bat
    echo echo Sistema RETIE iniciando...
    echo echo Acceso: http://localhost:5000
    echo python app.py
    echo pause
) > iniciar.bat

echo [OK] Script iniciar.bat creado
pause
