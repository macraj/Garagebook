#!/bin/bash
# Garagebook — launcher dla macOS (dwuklik w Finderze)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "Pierwsza instalacja — konfigurowanie środowiska..."
    bash scripts/macos/install.sh
    if [ $? -ne 0 ]; then
        echo "Instalacja nie powiodła się."
        read -p "Naciśnij Enter, aby zamknąć..."
        exit 1
    fi
fi

echo "Uruchamianie Garagebook..."
.venv/bin/python main.py

# Zamknij okno Terminala po wyjściu z aplikacji
osascript -e 'tell application "Terminal" to close first window' &>/dev/null
