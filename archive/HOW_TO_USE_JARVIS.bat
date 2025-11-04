@echo off
REM ============================================================
REM JARVIS - Easy Run Script
REM This script runs Jarvis with the correct Python interpreter
REM ============================================================
echo.
echo ============================================================
echo   JARVIS - Voice Assistant
echo ============================================================
echo.
echo Starting Jarvis...
echo (Using venv Python - all dependencies loaded)
echo.
echo ============================================================
echo.

REM Run Jarvis with venv Python
venv\Scripts\python.exe jarvis_simple.py

pause



