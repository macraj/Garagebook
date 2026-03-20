#!/bin/bash
# Garagebook — launcher dla Linux
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Zainstaluj zależności systemowe (GTK/WebKit) przy pierwszym uruchomieniu
if [ ! -f ".deps_installed" ]; then
    echo "Pierwsza instalacja — konfigurowanie zależności systemowych..."
    bash scripts/linux/install.sh
    if [ $? -ne 0 ]; then
        echo "Instalacja zależności nie powiodła się."
        read -p "Naciśnij Enter, aby zamknąć..."
        exit 1
    fi
    touch .deps_installed
fi

# Zainstaluj uv jeśli brak
if ! command -v uv &>/dev/null; then
    echo "Instalowanie menedżera pakietów (uv)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Na Linuxie potrzebujemy --system-site-packages dla PyGObject (GTK)
if [ ! -d ".venv" ]; then
    uv venv --system-site-packages --python 3.13
    uv sync
fi

echo "Uruchamianie Garagebook..."
uv run main.py
