@echo off
chcp 65001 >nul
title FORJIS - Quitar autoarranque
set "STARTUP=%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup"
del "%STARTUP%\FORJIS.lnk" >nul 2>&1
del "%STARTUP%\FORJIS.vbs" >nul 2>&1
echo  [OK] Autoarranque de FORJIS desactivado.
echo.
pause
