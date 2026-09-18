@echo off
cd /d "%~dp0"
".\env\Scripts\python.exe" "main.py"
if errorlevel 1 pause
