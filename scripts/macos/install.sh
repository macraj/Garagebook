#!/bin/bash
set -e
cd "$(dirname "$0")/../.."

echo ""
echo "=== Instalacja Garagebook (macOS) ==="
echo ""

# Zainstaluj uv jeśli brak
if ! command -v uv &>/dev/null; then
    echo "Instalowanie menedżera pakietów (uv)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.local/bin:$PATH"
fi

# Synchronizuj środowisko
echo "Konfigurowanie środowiska Python..."
uv sync

echo ""
echo "=== Instalacja zakończona pomyślnie! ==="
echo ""
