@echo off
cd /d "%~dp0..\.."

echo.
echo === Instalacja Garagebook (Windows) ===
echo.

:: Sprawdz WebView2 Runtime (wymagany przez pywebview)
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-235B8DE50529}" >nul 2>&1
if %ERRORLEVEL% neq 0 (
    reg query "HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-235B8DE50529}" >nul 2>&1
)
if %ERRORLEVEL% neq 0 (
    echo Instalowanie Microsoft Edge WebView2 Runtime...
    echo (wymagany do wyswietlania interfejsu aplikacji)
    powershell -ExecutionPolicy ByPass -c ^
        "Invoke-WebRequest -Uri 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile '%TEMP%\MicrosoftEdgeWebview2Setup.exe'; Start-Process '%TEMP%\MicrosoftEdgeWebview2Setup.exe' -ArgumentList '/silent /install' -Wait"
    if %ERRORLEVEL% neq 0 (
        echo UWAGA: Nie udalo sie zainstalowac WebView2 Runtime.
        echo Pobierz recznie ze strony: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
        echo.
    ) else (
        echo WebView2 Runtime zainstalowany pomyslnie.
    )
)

:: Zainstaluj uv jesli brak
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Instalowanie menedzera pakietow (uv)...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)

echo Konfigurowanie srodowiska Python...
uv sync

echo.
echo === Instalacja zakonczona pomyslnie! ===
echo.
pause
