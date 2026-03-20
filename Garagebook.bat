@echo off
setlocal
cd /d "%~dp0"

:: Sprawdz WebView2 Runtime
call :check_webview2
if %ERRORLEVEL% neq 0 (
    echo Brak Microsoft Edge WebView2 Runtime - uruchamiam instalacje...
    call scripts\windows\install.bat
)

:: Sprawdz uv
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Instalowanie menedzera pakietow ^(uv^)...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)

echo Uruchamianie Garagebook...
uv run main.py
exit /b 0


:check_webview2
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-235B8DE50529}" /v pv >nul 2>&1 && exit /b 0
reg query "HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-235B8DE50529}" /v pv >nul 2>&1 && exit /b 0
reg query "HKCU\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-235B8DE50529}" /v pv >nul 2>&1 && exit /b 0
exit /b 1
