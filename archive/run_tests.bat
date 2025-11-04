@echo off
echo Activating virtual environment...
call .\venv\Scripts\activate.bat

echo.
echo Running Sprint 7 tests...
echo.

python test_sprint7_all.py

echo.
pause



