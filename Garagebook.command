#!/bin/bash
# Garagebook — launcher dla macOS (dwuklik w Finderze)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Zainstaluj uv jeśli brak
if ! command -v uv &>/dev/null; then
    echo "Instalowanie menedżera pakietów (uv)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

echo "Uruchamianie Garagebook..."
uv run main.py

# Zamknij okno Terminala po wyjściu z aplikacji
osascript -e 'tell application "Terminal" to close first window' &>/dev/null
