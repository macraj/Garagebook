#!/bin/bash
set -e
cd "$(dirname "$0")/../.."

echo ""
echo "=== Instalacja Garagebook (Linux) ==="
echo ""

# Wykryj menedżer pakietów i zainstaluj zależności systemowe
if command -v apt-get &>/dev/null; then
    echo "Wykryto: apt (Debian/Ubuntu)"
    sudo apt-get update -q
    sudo apt-get install -y \
        python3-venv python3-pip \
        python3-gi python3-gi-cairo \
        gir1.2-gtk-3.0 libgtk-3-0 \
        gir1.2-webkit2-4.1 2>/dev/null || \
    sudo apt-get install -y \
        python3-venv python3-pip \
        python3-gi python3-gi-cairo \
        gir1.2-gtk-3.0 libgtk-3-0 \
        gir1.2-webkit2-4.0

elif command -v dnf &>/dev/null; then
    echo "Wykryto: dnf (Fedora/RHEL)"
    sudo dnf install -y \
        python3 python3-pip python3-gobject \
        gtk3 webkit2gtk4.1 2>/dev/null || \
    sudo dnf install -y \
        python3 python3-pip python3-gobject \
        gtk3 webkit2gtk3

elif command -v pacman &>/dev/null; then
    echo "Wykryto: pacman (Arch)"
    sudo pacman -S --noconfirm \
        python python-pip python-gobject \
        gtk3 webkit2gtk

else
    echo "BŁĄD: Nie rozpoznano menedżera pakietów (apt/dnf/pacman)."
    echo "Zainstaluj ręcznie: python3-gi, gtk3, webkit2gtk"
    exit 1
fi

# Usuń stare venv bez --system-site-packages (wymagane przez pywebview na Linuxie)
if [ -d ".venv" ] && ! grep -q "include-system-site-packages = true" .venv/pyvenv.cfg 2>/dev/null; then
    echo "Aktualizacja środowiska wirtualnego..."
    rm -rf .venv
fi

echo "Tworzenie środowiska wirtualnego (.venv)..."
python3 -m venv .venv --system-site-packages

echo "Instalowanie zależności Python..."
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt

echo ""
echo "=== Instalacja zakończona pomyślnie! ==="
echo ""
