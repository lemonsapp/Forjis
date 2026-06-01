@echo off
chcp 65001 >nul
title FORJIS - Test de microfono
cd /d "%~dp0"
echo IMPORTANTE: cerra FORJIS antes de correr este test (asi no pelean por el mic).
echo.
pause
".venv\Scripts\python.exe" mic_test.py
