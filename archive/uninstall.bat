@echo off
echo ============================================================
echo  JARVIS - Uninstaller
echo ============================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This uninstaller requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

set "INSTALL_DIR=C:\Program Files\Jarvis"

echo Uninstalling Jarvis...
echo.

REM Remove shortcuts
echo Removing shortcuts...
del "%USERPROFILE%\Desktop\Jarvis.lnk" >nul 2>&1
rmdir /S /Q "%APPDATA%\Microsoft\Windows\Start Menu\Programs\Jarvis" >nul 2>&1

echo Removing files...
if exist "%INSTALL_DIR%" (
    rmdir /S /Q "%INSTALL_DIR%" >nul 2>&1
    echo   - Removed: %INSTALL_DIR%
)

echo.
echo ============================================================
echo  Uninstallation Complete!
echo ============================================================
echo.
echo Jarvis has been removed from your system.
echo.
pause




