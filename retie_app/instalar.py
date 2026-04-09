#!/usr/bin/env python3
"""
RETIE Manager - Script de Instalación
Instala las dependencias y configura el entorno del sistema.
"""

import subprocess
import sys
import os
import platform


def print_banner():
    print("=" * 60)
    print("  ⚡  RETIE Manager — Instalador v1.0")
    print("  Gestión de Proyectos Eléctricos y Fotovoltaicos")
    print("  Normativa RETIE Colombia")
    print("=" * 60)
    print()


def check_python():
    version = sys.version_info
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} detectado")
    if version.major < 3 or (version.major == 3 and version.minor < 9):
        print("❌ Se requiere Python 3.9 o superior.")
        sys.exit(1)


def install_packages():
    packages = [
        "PySide6",
        "python-docx",
    ]
    print("\nInstalando dependencias...")
    for pkg in packages:
        print(f"  Instalando {pkg}...", end=" ", flush=True)
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", pkg, "--quiet"],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            print("✓")
        else:
            print(f"❌ Error: {result.stderr}")


def create_launcher():
    """Crea un script launcher para el sistema operativo actual."""
    app_dir = os.path.dirname(os.path.abspath(__file__))
    main_py = os.path.join(app_dir, "main.py")
    sistema = platform.system()

    if sistema == "Windows":
        # Archivo .bat
        bat = f"""@echo off
cd /d "{app_dir}"
python main.py
pause
"""
        ruta = os.path.join(app_dir, "RETIE_Manager.bat")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(bat)
        print(f"✓ Launcher creado: {ruta}")

        # Shortcut en escritorio
        escritorio = os.path.join(os.path.expanduser("~"), "Desktop")
        if os.path.exists(escritorio):
            shortcut = os.path.join(escritorio, "RETIE Manager.bat")
            with open(shortcut, "w", encoding="utf-8") as f:
                f.write(bat)
            print(f"✓ Acceso directo creado en escritorio")

    elif sistema in ("Linux", "Darwin"):
        sh = f"""#!/bin/bash
cd "{app_dir}"
python3 main.py
"""
        ruta = os.path.join(app_dir, "retie_manager.sh")
        with open(ruta, "w") as f:
            f.write(sh)
        os.chmod(ruta, 0o755)
        print(f"✓ Launcher creado: {ruta}")


def init_database():
    """Inicializa la base de datos."""
    print("\nInicializando base de datos...", end=" ", flush=True)
    try:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from core.database import initialize_database
        initialize_database()
        print("✓")
    except Exception as e:
        print(f"❌ Error: {e}")


def main():
    print_banner()
    check_python()
    install_packages()
    init_database()
    create_launcher()

    print()
    print("=" * 60)
    print("✅  Instalación completada exitosamente!")
    print()
    print("  Credenciales por defecto:")
    print("    Usuario:     admin")
    print("    Contraseña:  admin123")
    print()
    print("  Para iniciar la aplicación:")
    if platform.system() == "Windows":
        print("    Doble clic en RETIE_Manager.bat")
        print("    O ejecutar: python main.py")
    else:
        print("    ./retie_manager.sh")
        print("    O ejecutar: python3 main.py")
    print("=" * 60)


if __name__ == "__main__":
    main()
