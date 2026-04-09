@echo off
setlocal ENABLEDELAYEDEXPANSION

rem ============================================================
rem  Script de construcción para GeoInventario
rem  Genera un ejecutable .exe con interfaz gráfica (sin consola)
rem  y lo guarda en la carpeta "App GeoInventario"
rem ============================================================

rem Ir a la carpeta del proyecto (donde está este .bat)
cd /d "%~dp0"
set ROOT_DIR=%CD%

rem Activar entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
) else (
    echo No se encontro el entorno virtual en "venv".
    echo Crea el entorno virtual y ejecuta: pip install -r requirements.txt
    pause
    exit /b 1
)

rem Instalar dependencias necesarias
echo Instalando dependencias de Python...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

rem Verificar que PyInstaller este instalado
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller...
    python -m pip install pyinstaller
)

rem Limpiar construcciones anteriores
if exist "build" (
    rmdir /s /q "build"
)

rem Crear carpeta de salida si no existe
if not exist "App GeoInventario" (
    mkdir "App GeoInventario"
)

echo.
echo Construyendo ejecutable GeoInventario...

rem Ejecutar PyInstaller en una sola linea para evitar errores de sintaxis
pyinstaller --noconfirm --clean --windowed ^
 --name "GeoInventario" ^
 --distpath "App GeoInventario" ^
 --workpath "build" ^
 --specpath "build" ^
 --add-data "%ROOT_DIR%\database;database" ^
 --add-data "%ROOT_DIR%\documentos;documentos" ^
 --add-data "%ROOT_DIR%\Plantilla_GeoInventario.xlsx;." ^
 --add-data "%ROOT_DIR%\Plantilla_Herramientas_GeoInventario.xlsx;." ^
 app\main.py

if errorlevel 1 (
    echo.
    echo Ocurrio un error al generar el ejecutable.
    pause
    exit /b 1
)

echo.
echo ============================================================
echo  Construccion completada.
echo  Ejecutable generado en: "App GeoInventario\GeoInventario\GeoInventario.exe"
echo ============================================================
echo.
pause

