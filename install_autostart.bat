@echo off
chcp 65001 >nul
title FORJIS - Autoarranque
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
REM limpiar entradas viejas
del "%STARTUP%\FORJIS.vbs" >nul 2>&1
REM crear acceso directo en Inicio que apunta al lanzador (rutas dinámicas)
powershell -NoProfile -Command "$ws=New-Object -ComObject WScript.Shell; $l=$ws.CreateShortcut('%STARTUP%\FORJIS.lnk'); $l.TargetPath='%~dp0start_hidden.vbs'; $l.WorkingDirectory='%~dp0'; $l.Save()"
if exist "%STARTUP%\FORJIS.lnk" (
  echo  [OK] FORJIS se abrira solo al prender la PC.
  echo       Para desactivarlo: uninstall_autostart.bat
) else (
  echo  [ERROR] No se pudo crear el autoarranque.
)
echo.
pause
