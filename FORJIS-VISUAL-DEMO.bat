@echo off
title FORJIS HUD (modo visual / sin microfono)
cd /d "%~dp0"
set FORJIS_MOCK=1
start "" http://localhost:8000
".venv\Scripts\python.exe" server.py
pause
