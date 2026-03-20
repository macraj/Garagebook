@echo off
cd /d "%~dp0"

where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Instalowanie menedzera pakietow (uv)...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)

echo Uruchamianie Garagebook...
uv run main.py
