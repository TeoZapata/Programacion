#!/bin/bash
# ==============================================================
# instalar.sh
# Script de instalación del Sistema RETIE en Linux/Ubuntu
# ==============================================================

set -e  # Detener en caso de error

echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║     SISTEMA DE CERTIFICADOS RETIE - INSTALACIÓN    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""

# ── Colores ────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

ok() { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${BLUE}ℹ️  $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err() { echo -e "${RED}❌ $1${NC}"; }

# ── 1. Verificar Python ────────────────────────────────────
info "Verificando Python 3..."
if ! command -v python3 &> /dev/null; then
    err "Python 3 no encontrado. Instalando..."
    sudo apt-get update && sudo apt-get install -y python3 python3-pip python3-venv
fi
PYTHON_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
ok "Python $PYTHON_VER encontrado"

# ── 2. Instalar dependencias del sistema ───────────────────
info "Instalando dependencias del sistema..."
sudo apt-get update -qq
sudo apt-get install -y -qq \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1
ok "Dependencias del sistema instaladas"

# ── 3. Crear entorno virtual ───────────────────────────────
info "Creando entorno virtual Python..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    ok "Entorno virtual creado"
else
    warn "Entorno virtual ya existe, omitiendo..."
fi

# Activar entorno
source venv/bin/activate

# ── 4. Instalar dependencias Python ───────────────────────
info "Instalando dependencias Python (puede tomar varios minutos)..."
pip install --upgrade pip -q
pip install -r requirements.txt -q
ok "Dependencias Python instaladas"

# ── 5. Crear directorios ───────────────────────────────────
info "Creando estructura de directorios..."
mkdir -p uploads/pdf uploads/images
ok "Directorios creados"

# ── 6. Crear archivo .env ──────────────────────────────────
if [ ! -f ".env" ]; then
    info "Creando archivo de configuración .env..."
    cat > .env << 'EOF'
# Configuración del Sistema RETIE
FLASK_ENV=development
FLASK_DEBUG=false
SECRET_KEY=retie-2024-cambiar-esta-clave-en-produccion
HOST=0.0.0.0
PORT=5000

# Base de datos (SQLite para desarrollo local)
# Para PostgreSQL: postgresql://usuario:password@localhost:5432/retie_db
DATABASE_URL=sqlite:///retie_dev.db

# Tesseract OCR
TESSERACT_CMD=/usr/bin/tesseract
EOF
    ok "Archivo .env creado"
else
    warn "Archivo .env ya existe"
fi

# ── 7. Inicializar base de datos ───────────────────────────
info "Inicializando base de datos..."
python3 -c "
from app import create_app
app = create_app('development')
with app.app_context():
    print('Base de datos inicializada')
"
ok "Base de datos lista"

# ── 8. Verificar Tesseract ─────────────────────────────────
if command -v tesseract &> /dev/null; then
    TESS_VER=$(tesseract --version 2>&1 | head -1)
    ok "Tesseract OCR: $TESS_VER"
else
    warn "Tesseract no encontrado. El OCR no estará disponible."
fi

# ── Resumen final ──────────────────────────────────────────
echo ""
echo "╔════════════════════════════════════════════════════╗"
echo "║            INSTALACIÓN COMPLETADA ✅               ║"
echo "╠════════════════════════════════════════════════════╣"
echo "║                                                    ║"
echo "║  Para iniciar el sistema:                          ║"
echo "║                                                    ║"
echo "║    source venv/bin/activate                        ║"
echo "║    python app.py                                   ║"
echo "║                                                    ║"
echo "║  Acceso:  http://localhost:5000                    ║"
echo "║  Red:     http://<TU-IP>:5000                      ║"
echo "║                                                    ║"
echo "║  Usuario inicial: admin                            ║"
echo "║  Contraseña:      admin123                         ║"
echo "║                                                    ║"
echo "╚════════════════════════════════════════════════════╝"
echo ""
