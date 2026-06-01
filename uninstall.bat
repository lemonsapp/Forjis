@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
cd /d "%~dp0"
set "PROJ=%~dp0"
title  FORJIS - Desinstalador
cls
echo ============================================================
echo            D E S I N S T A L A D O R   F O R J I S
echo ============================================================
echo.
echo  Esto ELIMINA FORJIS de esta PC:
echo    - Cierra FORJIS si esta abierto
echo    - Borra el acceso directo del Escritorio
echo    - Quita el autoarranque con Windows
echo    - Borra el modelo de voz (Whisper) cacheado
echo    - (opcional) Desinstala Ollama y el modelo local
echo    - Borra ESTA carpeta del proyecto:
echo         %PROJ%
echo.
echo  [!] Accion IRREVERSIBLE. Se pierden api_key.txt, memoria y estado.
echo.
set "OK="
set /p "OK=Escribi BORRAR y Enter para confirmar (otra cosa = cancelar): "
if /i not "!OK!"=="BORRAR" ( echo. & echo Cancelado. No se toco nada. & echo. & pause & exit /b )
echo.

REM --- 1) Cerrar FORJIS ---
echo [1/5] Cerrando FORJIS...
taskkill /f /im pythonw.exe >nul 2>&1
echo     OK
echo.

REM --- 2) Acceso directo del Escritorio ---
echo [2/5] Borrando acceso directo del Escritorio...
del /f /q "%USERPROFILE%\Desktop\FORJIS.lnk" >nul 2>&1
echo     OK
echo.

REM --- 3) Autoarranque ---
echo [3/5] Quitando autoarranque con Windows...
del /f /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\FORJIS.vbs" >nul 2>&1
del /f /q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\FORJIS.lnk" >nul 2>&1
echo     OK
echo.

REM --- 4) Modelo de voz (Whisper) cacheado en HuggingFace ---
echo [4/5] Borrando modelos de voz cacheados...
for /d %%D in ("%USERPROFILE%\.cache\huggingface\hub\models--Systran--faster-whisper-*") do rmdir /s /q "%%D" >nul 2>&1
echo     OK
echo.

REM --- 5) Ollama (opcional) ---
echo [5/5] Cerebro local (Ollama)...
set "DELOLL="
set /p "DELOLL=Borrar tambien Ollama y el modelo qwen2.5:7b? (s/n): "
if /i "!DELOLL!"=="s" (
  taskkill /f /im ollama.exe >nul 2>&1
  ollama rm qwen2.5:7b >nul 2>&1
  winget uninstall -e --id Ollama.Ollama --accept-source-agreements >nul 2>&1
  rmdir /s /q "%USERPROFILE%\.ollama" >nul 2>&1
  echo     Ollama y el modelo eliminados.
) else (
  echo     Ollama lo dejo instalado (lo podes usar para otra cosa).
)
echo.

echo ============================================================
echo    Listo. Se borra la carpeta del proyecto y se cierra.
echo ============================================================
echo.
echo (Si quedan archivos por estar en uso, borra la carpeta a mano:)
echo   %PROJ%
echo.
timeout /t 3 /nobreak >nul

REM --- Autodestruccion: salimos del script y borramos la carpeta ---
cd /d "%USERPROFILE%"
(goto) 2>nul & rmdir /s /q "%PROJ%"
