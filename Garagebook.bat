@echo off
cd /d "%~dp0"

if not exist ".venv" (
    echo Pierwsza instalacja - konfigurowanie srodowiska...
    call scripts\windows\install.bat
    if %ERRORLEVEL% neq 0 (
        echo Instalacja nie powiodla sie.
        pause
        exit /b 1
    )
)

echo Uruchamianie Garagebook...
.venv\Scripts\python main.py
