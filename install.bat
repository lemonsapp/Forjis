@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
title  FORJIS - Instalador
cd /d "%~dp0"
cls
echo ============================================================
echo                  I N S T A L A D O R   F O R J I S
echo            Tu propio sistema JARVIS de Iron Man
echo ============================================================
echo.

REM ---------- 1) Python ----------
echo [1/6] Verificando Python...
set "PY="
python --version >nul 2>&1 && set "PY=python"
if not defined PY ( py -3 --version >nul 2>&1 && set "PY=py -3" )
if not defined PY (
  echo     Python no esta instalado. Intento instalarlo con winget...
  winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements
  echo.
  echo     [!] Si recien se instalo Python, CERRA esta ventana y volve a
  echo         ejecutar install.bat para continuar.
  echo.
  pause
  exit /b
)
echo     OK ^(%PY%^)
echo.

REM ---------- 2) Entorno ----------
echo [2/6] Creando entorno aislado (.venv)...
%PY% -m venv .venv
set "VPY=.venv\Scripts\python.exe"
if not exist "%VPY%" ( echo     [ERROR] No se pudo crear el entorno. & pause & exit /b )
echo     OK
echo.

REM ---------- 3) Dependencias ----------
echo [3/6] Instalando dependencias ^(puede tardar varios minutos^)...
"%VPY%" -m pip install --upgrade pip >nul
"%VPY%" -m pip install -r requirements.txt
echo     OK
echo.

REM ---------- 4) Modelos ----------
echo [4/6] Descargando modelos de voz y vision...
"%VPY%" download_models.py
echo.

REM ---------- 5) API key ----------
echo [5/6] Configurando el cerebro ^(API de Claude^)...
if exist api_key.txt (
  echo     Ya existe api_key.txt, la dejo como esta.
) else (
  echo     Necesitas una API key de Anthropic.
  echo     Sacala gratis en:  https://console.anthropic.com  -^>  API Keys
  echo.
  set /p "APIKEY=    Pega tu API key y Enter (o deja vacio para hacerlo despues): "
  if not "!APIKEY!"=="" (
    <nul set /p "=!APIKEY!" > api_key.txt
    echo     Clave guardada en api_key.txt
  ) else (
    echo     Saltado. Despues crea api_key.txt y pega ahi tu clave.
  )
)
echo.

REM ---------- 6) Acceso directo ----------
echo [6/6] Creando acceso directo FORJIS en el Escritorio...
powershell -NoProfile -Command "$ws=New-Object -ComObject WScript.Shell; $l=$ws.CreateShortcut([Environment]::GetFolderPath('Desktop')+'\FORJIS.lnk'); $l.TargetPath='%CD%\.venv\Scripts\pythonw.exe'; $l.Arguments='app.py'; $l.WorkingDirectory='%CD%'; $l.IconLocation='%SystemRoot%\System32\shell32.dll,13'; $l.Description='FORJIS - asistente JARVIS'; $l.Save()"
echo     OK
echo.

echo ============================================================
echo    LISTO!  FORJIS quedo instalado.
echo.
echo    - Abrilo con el icono FORJIS del Escritorio
echo    - Que arranque solo al prender la PC:  install_autostart.bat
echo    - Decile "FORJIS, que hora es" o aplaudi dos veces
echo ============================================================
echo.
set /p "RUN=Queres abrir FORJIS ahora? (s/n): "
if /i "!RUN!"=="s" start "" ".venv\Scripts\pythonw.exe" app.py
echo.
pause
