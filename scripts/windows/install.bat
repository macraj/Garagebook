@echo off
setlocal
cd /d "%~dp0..\.."

echo.
echo === Instalacja Garagebook (Windows) ===
echo.

:: Sprawdz WebView2 Runtime (wymagany przez pywebview)
call :check_webview2
if %ERRORLEVEL% neq 0 call :install_webview2

:: Zainstaluj uv jesli brak
where uv >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo Instalowanie menedzera pakietow ^(uv^)...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    set "PATH=%USERPROFILE%\.local\bin;%PATH%"
)

echo Konfigurowanie srodowiska Python...
uv sync

echo.
echo === Instalacja zakonczona pomyslnie! ===
echo.
pause
exit /b 0


:check_webview2
reg query "HKLM\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-235B8DE50529}" /v pv >nul 2>&1 && exit /b 0
reg query "HKLM\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-235B8DE50529}" /v pv >nul 2>&1 && exit /b 0
reg query "HKCU\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BEB-235B8DE50529}" /v pv >nul 2>&1 && exit /b 0
exit /b 1


:install_webview2
echo Instalowanie Microsoft Edge WebView2 Runtime...
echo Wymagany do wyswietlania interfejsu aplikacji.
set "WV2_INSTALLER=%TEMP%\MicrosoftEdgeWebview2Setup.exe"
powershell -ExecutionPolicy ByPass -c "Invoke-WebRequest -Uri 'https://go.microsoft.com/fwlink/p/?LinkId=2124703' -OutFile '%WV2_INSTALLER%'"
if not exist "%WV2_INSTALLER%" (
    echo UWAGA: Nie udalo sie pobrac WebView2 Runtime.
    echo Pobierz recznie: https://developer.microsoft.com/en-us/microsoft-edge/webview2/
    exit /b 1
)
"%WV2_INSTALLER%" /silent /install
echo WebView2 Runtime zainstalowany.
exit /b 0
