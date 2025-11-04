@echo off
REM ============================================================
REM JARVIS Launcher
REM ============================================================
echo.
echo Starting Jarvis...
echo.

REM Activate venv and run Jarvis
call venv\Scripts\Activate.bat
python jarvis_simple.py

pause



