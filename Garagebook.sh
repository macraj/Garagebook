#!/bin/bash
# Garagebook — launcher dla Linux
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "Pierwsza instalacja — konfigurowanie środowiska..."
    bash scripts/linux/install.sh
    if [ $? -ne 0 ]; then
        echo "Instalacja nie powiodła się."
        read -p "Naciśnij Enter, aby zamknąć..."
        exit 1
    fi
fi

echo "Uruchamianie Garagebook..."
.venv/bin/python main.py
