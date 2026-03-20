@echo off
cd /d "%~dp0"

:: Sprawdz WebView2 Runtime (wymagany przez pywebview)
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-235B8DE50529}" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    reg query "HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-235B8DE50529}" >nul 2>&1
)
if %ERRORLEVEL% neq 0 (
    echo Brak Microsoft Edge WebView2 Runtime - uruchamiam instalacje...
    call scripts\windows\install.bat
)

where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Instalowanie menedzera pakietow (uv)...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)

echo Uruchamianie Garagebook...
uv run main.py
