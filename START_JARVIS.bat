@echo off
cls
echo.
echo ======================================================
echo    JARVIS - Modern AI Voice Assistant
echo ======================================================
echo.
echo  Starting Jarvis...
echo.
echo  Features:
echo   - Voice Input (5-second recording)
echo   - Text-to-Speech (Audio responses)
echo   - 157 Intent Types
echo   - Flexible command patterns
echo.
echo ======================================================
echo.

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run Jarvis
python jarvis_simple_working.py

pause

