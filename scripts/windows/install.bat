@echo off
cd /d "%~dp0..\.."

echo.
echo === Instalacja Garagebook (Windows) ===
echo.

where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo BLAD: Python nie jest zainstalowany lub nie jest w PATH.
    echo Pobierz ze strony: https://www.python.org/downloads/
    echo Podczas instalacji zaznacz opcje "Add Python to PATH"
    pause
    exit /b 1
)

echo Tworzenie srodowiska wirtualnego (.venv)...
python -m venv .venv

echo Instalowanie zaleznosci Python...
.venv\Scripts\pip install --upgrade pip -q
.venv\Scripts\pip install -r requirements.txt

echo.
echo === Instalacja zakonczona pomyslnie! ===
echo.
pause
