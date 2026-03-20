#!/bin/bash
set -e
cd "$(dirname "$0")/../.."

echo ""
echo "=== Instalacja Garagebook (Linux) ==="
echo ""

# Wykryj menedżer pakietów i zainstaluj zależności systemowe (GTK/WebKit)
if command -v apt-get &>/dev/null; then
    echo "Wykryto: apt (Debian/Ubuntu)"
    sudo apt-get update -q
    sudo apt-get install -y \
        python3-gi python3-gi-cairo \
        gir1.2-gtk-3.0 libgtk-3-0 \
        gir1.2-webkit2-4.1 2>/dev/null || \
    sudo apt-get install -y \
        python3-gi python3-gi-cairo \
        gir1.2-gtk-3.0 libgtk-3-0 \
        gir1.2-webkit2-4.0

elif command -v dnf &>/dev/null; then
    echo "Wykryto: dnf (Fedora/RHEL)"
    sudo dnf install -y \
        python3-gobject gtk3 webkit2gtk4.1 2>/dev/null || \
    sudo dnf install -y \
        python3-gobject gtk3 webkit2gtk3

elif command -v pacman &>/dev/null; then
    echo "Wykryto: pacman (Arch)"
    sudo pacman -S --noconfirm \
        python-gobject gtk3 webkit2gtk

else
    echo "BŁĄD: Nie rozpoznano menedżera pakietów (apt/dnf/pacman)."
    echo "Zainstaluj ręcznie: python3-gi, gtk3, webkit2gtk"
    exit 1
fi

# Zainstaluj uv jeśli brak
if ! command -v uv &>/dev/null; then
    echo "Instalowanie menedżera pakietów (uv)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Na Linuxie potrzebujemy --system-site-packages dla PyGObject (GTK)
echo "Konfigurowanie środowiska Python..."
uv venv --system-site-packages --python 3.13
uv sync

echo ""
echo "=== Instalacja zakończona pomyślnie! ==="
echo ""
