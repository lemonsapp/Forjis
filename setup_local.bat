@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title  FORJIS - Cerebro LOCAL (Ollama)

REM Uso: setup_local.bat            (interactivo, con pausa al final)
REM      setup_local.bat quiet      (lo llama el instalador, sin pausa)
set "QUIET=%~1"

set "VPY=.venv\Scripts\python.exe"

echo ============================================================
echo            FORJIS - Cerebro LOCAL (gratis y offline)
echo ============================================================
echo.

REM Dejar elegido el modo local desde ya (aunque falte bajar el modelo)
if exist "%VPY%" "%VPY%" -c "import state; state.set('brain','local')" 2>nul

REM ---------- 1) Ollama ----------
echo [1/2] Verificando Ollama (el motor del LLM local)...
where ollama >nul 2>&1
if errorlevel 1 (
  echo     No esta instalado. Lo instalo con winget...
  winget install -e --id Ollama.Ollama --accept-package-agreements --accept-source-agreements
  echo.
  where ollama >nul 2>&1
  if errorlevel 1 (
    echo     [!] Ollama se instalo pero todavia no esta en el PATH de esta ventana.
    echo         CERRA esta ventana, abri una NUEVA y volve a ejecutar setup_local.bat
    echo.
    if /i not "%QUIET%"=="quiet" pause
    exit /b
  )
)
echo     OK
echo.

REM ---------- 2) Modelo ----------
echo [2/2] Descargando el modelo qwen2.5:7b (~4.7 GB)... puede tardar varios minutos.
echo     (es de una sola vez; despues queda cacheado en tu PC)
ollama pull qwen2.5:7b
if errorlevel 1 (
  echo.
  echo     [!] No pude descargar el modelo. Fijate que Ollama este corriendo
  echo         (icono en la bandeja) e intenta de nuevo:  ollama pull qwen2.5:7b
  echo.
  if /i not "%QUIET%"=="quiet" pause
  exit /b
)
echo.
echo ============================================================
echo    LISTO!  FORJIS quedo en modo LOCAL (100%% gratis y offline).
echo    Podes cambiar a Claude cuando quieras desde el boton de la HUD.
echo ============================================================
echo.
if /i not "%QUIET%"=="quiet" pause
