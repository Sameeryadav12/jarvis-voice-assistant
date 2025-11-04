@echo off
echo ============================================================
echo  JARVIS - Windows Installer
echo ============================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo ERROR: This installer requires administrator privileges.
    echo Please right-click and select "Run as administrator"
    pause
    exit /b 1
)

echo Installing Jarvis...
echo.

REM Create installation directory
set "INSTALL_DIR=C:\Program Files\Jarvis"
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"

echo Copying files...
copy /Y dist\jarvis.exe "%INSTALL_DIR%\jarvis.exe" >nul
if not exist "%INSTALL_DIR%\config" mkdir "%INSTALL_DIR%\config"
copy /Y config\settings.yaml "%INSTALL_DIR%\config\settings.yaml" >nul 2>&1
copy /Y config\settings.example.yaml "%INSTALL_DIR%\config\settings.example.yaml" >nul 2>&1
copy /Y README.md "%INSTALL_DIR%\README.md" >nul 2>&1

echo Creating desktop shortcut...
set "DESKTOP=%USERPROFILE%\Desktop"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $S = $WS.CreateShortcut('%DESKTOP%\Jarvis.lnk'); $S.TargetPath = '%INSTALL_DIR%\jarvis.exe'; $S.WorkingDirectory = '%INSTALL_DIR%'; $S.IconLocation = '%INSTALL_DIR%\jarvis.exe,0'; $S.Description = 'Jarvis Voice Assistant'; $S.Save()"

echo Creating start menu shortcut...
set "START_MENU=%APPDATA%\Microsoft\Windows\Start Menu\Programs"
if not exist "%START_MENU%\Jarvis" mkdir "%START_MENU%\Jarvis"
powershell -Command "$WS = New-Object -ComObject WScript.Shell; $S = $WS.CreateShortcut('%START_MENU%\Jarvis\Jarvis.lnk'); $S.TargetPath = '%INSTALL_DIR%\jarvis.exe'; $S.WorkingDirectory = '%INSTALL_DIR%'; $S.IconLocation = '%INSTALL_DIR%\jarvis.exe,0'; $S.Description = 'Jarvis Voice Assistant'; $S.Save()"

echo.
echo ============================================================
echo  Installation Complete!
echo ============================================================
echo.
echo Jarvis has been installed to:
echo   %INSTALL_DIR%
echo.
echo Desktop shortcut created: Jarvis.lnk
echo Start menu entry created: Programs\Jarvis
echo.
echo To run Jarvis:
echo   1. Double-click "Jarvis.lnk" on your desktop
echo   2. Or find it in the Start menu under "Jarvis"
echo.
pause




