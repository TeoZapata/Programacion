#!/usr/bin/env bash
set -euo pipefail

echo "==> Diagnostico e instalacion de dependencias Qt/XCB para PySide6"

if [[ "${EUID}" -eq 0 ]]; then
  SUDO=""
else
  SUDO="sudo"
fi

WORKDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

if [[ -f /etc/os-release ]]; then
  # shellcheck disable=SC1091
  source /etc/os-release
  DISTRO_ID="${ID:-unknown}"
  DISTRO_LIKE="${ID_LIKE:-}"
else
  DISTRO_ID="unknown"
  DISTRO_LIKE=""
fi

install_apt() {
  echo "==> Detectado sistema tipo Debian/Ubuntu"
  $SUDO apt update
  $SUDO apt install -y \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    libgl1-mesa-glx
}

install_dnf() {
  echo "==> Detectado sistema tipo Fedora/RHEL"
  $SUDO dnf install -y \
    xcb-util-cursor \
    libxkbcommon-x11 \
    xcb-util-wm \
    xcb-util-image \
    xcb-util-keysyms \
    xcb-util-renderutil \
    libXcursor \
    mesa-libGL
}

install_pacman() {
  echo "==> Detectado sistema tipo Arch"
  $SUDO pacman -Sy --noconfirm \
    xcb-util-cursor \
    xcb-util-wm \
    xcb-util-image \
    xcb-util-keysyms \
    xcb-util-renderutil \
    libxkbcommon-x11 \
    mesa
}

install_zypper() {
  echo "==> Detectado sistema tipo openSUSE"
  $SUDO zypper install -y \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-render-util0 \
    libxcb-xinerama0 \
    Mesa-libGL1
}

case "${DISTRO_ID}" in
  ubuntu|debian|linuxmint|pop)
    install_apt
    ;;
  fedora|rhel|centos|rocky|almalinux)
    install_dnf
    ;;
  arch|manjaro|endeavouros)
    install_pacman
    ;;
  opensuse*|sles)
    install_zypper
    ;;
  *)
    if [[ "${DISTRO_LIKE}" == *debian* ]]; then
      install_apt
    elif [[ "${DISTRO_LIKE}" == *fedora* || "${DISTRO_LIKE}" == *rhel* ]]; then
      install_dnf
    elif [[ "${DISTRO_LIKE}" == *arch* ]]; then
      install_pacman
    else
      echo "No pude detectar automaticamente tu distro."
      echo "Instala manualmente paquetes equivalentes a:"
      echo "  libxcb-cursor0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-image0"
      echo "  libxcb-keysyms1 libxcb-render-util0 libxcb-xinerama0 libgl1-mesa-glx"
      exit 1
    fi
    ;;
esac

echo "==> Dependencias instaladas"

if grep -qi microsoft /proc/version 2>/dev/null; then
  echo "==> Detectado posible entorno WSL"
  echo "    Asegurate de tener WSLg o un servidor X funcional."
fi

if [[ -z "${DISPLAY:-}" && -z "${WAYLAND_DISPLAY:-}" ]]; then
  echo "==> Advertencia: no detecto DISPLAY ni WAYLAND_DISPLAY."
  echo "    Si estas en servidor, Docker o shell sin GUI, Qt no podra abrir ventanas."
fi

echo "==> Probando import de PySide6"
python3 - <<'PY'
from PySide6.QtCore import QLibraryInfo
print("PySide6 OK")
print("Plugins path:", QLibraryInfo.path(QLibraryInfo.LibraryPath.PluginsPath))
PY

echo "==> Puedes probar la app con:"
echo "    cd \"$WORKDIR\""
echo "    QT_QPA_PLATFORM=xcb python3 app/main.py"
