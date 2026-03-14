#!/bin/bash
set -e
cd "$(dirname "$0")/../.."

echo ""
echo "=== Instalacja Garagebook (macOS) ==="
echo ""

# Sprawdź Python 3.10+
if ! command -v python3 &>/dev/null; then
    echo "BŁĄD: Python 3 nie jest zainstalowany."
    echo "Pobierz ze strony: https://www.python.org/downloads/"
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJOR=$(python3 -c "import sys; print(sys.version_info.major)")
PY_MINOR=$(python3 -c "import sys; print(sys.version_info.minor)")

echo "Python $PY_VER znaleziony."

if [ "$PY_MAJOR" -lt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -lt 10 ]; }; then
    echo "BŁĄD: Wymagany Python 3.10 lub nowszy (znaleziono $PY_VER)."
    exit 1
fi

# Utwórz środowisko wirtualne
echo "Tworzenie środowiska wirtualnego (.venv)..."
python3 -m venv .venv

# Zainstaluj zależności
echo "Instalowanie zależności Python..."
.venv/bin/pip install --upgrade pip -q
.venv/bin/pip install -r requirements.txt

echo ""
echo "=== Instalacja zakończona pomyślnie! ==="
echo ""
