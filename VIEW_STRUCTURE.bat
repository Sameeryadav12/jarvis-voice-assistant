@echo off
cls
echo.
echo ==================================================================
echo               JARVIS PROJECT STRUCTURE
echo ==================================================================
echo.
echo  Root Directory:
echo.
tree /F /A | findstr /V "venv __pycache__ .pyc chroma_db tts_cache logs archive"
echo.
echo ==================================================================
echo.
echo  Documentation organized in docs/ folder!
echo.
echo  Open: docs\README.md for complete documentation index
echo.
echo ==================================================================
echo.
pause

