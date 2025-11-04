@echo off
cls
echo.
echo ==================================================================
echo        PROFESSIONAL ROOT CLEANUP
echo ==================================================================
echo.
echo  This will move old documentation files to archive folder
echo  and create a CLEAN, PROFESSIONAL root directory.
echo.
echo  What will be KEPT in root:
echo     - README.md (GitHub landing page)
echo     - LICENSE
echo     - requirements.txt
echo     - .gitignore
echo     - START_JARVIS.bat (launcher)
echo     - jarvis_simple_working.py (main app)
echo     - simple_tts.py (TTS module)
echo     - CHECK_EVERYTHING.py (verification)
echo     - docs/ folder (all documentation)
echo     - core/ folder (source code)
echo.
echo  What will be MOVED to archive/:
echo     - All SPRINT*.md files
echo     - All old status/summary files
echo     - All test result files
echo     - Old duplicate documentation
echo     - Development history files
echo.
echo ==================================================================
echo.
set /p confirm="Clean up root directory? This will make it professional! (yes/no): "

if /i "%confirm%"=="yes" (
    echo.
    echo Moving old documentation to archive...
    echo.
    
    REM Create archive subfolders
    if not exist "archive\sprints" mkdir "archive\sprints"
    if not exist "archive\old-docs" mkdir "archive\old-docs"
    if not exist "archive\test-results" mkdir "archive\test-results"
    if not exist "archive\old-status" mkdir "archive\old-status"
    
    REM Move SPRINT files
    echo Moving SPRINT files...
    move /Y SPRINT*.md "archive\sprints\" 2>nul
    move /Y ALL_SPRINTS*.md "archive\sprints\" 2>nul
    move /Y NEXT_SPRINT*.md "archive\sprints\" 2>nul
    
    REM Move TEST result files
    echo Moving TEST result files...
    move /Y TEST*.md "archive\test-results\" 2>nul
    move /Y TESTING*.md "archive\test-results\" 2>nul
    move /Y VERIFICATION*.md "archive\test-results\" 2>nul
    move /Y DEMO_RESULTS.md "archive\test-results\" 2>nul
    
    REM Move STATUS files
    echo Moving STATUS files...
    move /Y *STATUS*.md "archive\old-status\" 2>nul
    move /Y *COMPLETE*.md "archive\old-status\" 2>nul
    move /Y *SUMMARY*.md "archive\old-status\" 2>nul
    move /Y *FINAL*.md "archive\old-status\" 2>nul
    move /Y *SUCCESS*.md "archive\old-status\" 2>nul
    move /Y *FIXED*.md "archive\old-status\" 2>nul
    move /Y *ISSUES*.md "archive\old-status\" 2>nul
    
    REM Move old duplicate documentation
    echo Moving old duplicate documentation...
    move /Y README_*.md "archive\old-docs\" 2>nul
    move /Y QUICKSTART*.md "archive\old-docs\" 2>nul
    move /Y INSTALLATION*.md "archive\old-docs\" 2>nul
    move /Y CONTRIBUTING*.md "archive\old-docs\" 2>nul
    move /Y FEATURES.md "archive\old-docs\" 2>nul
    move /Y FILE_GUIDE.md "archive\old-docs\" 2>nul
    move /Y CHALLENGES.md "archive\old-docs\" 2>nul
    move /Y ROADMAP.md "archive\old-docs\" 2>nul
    move /Y PROJECT_SUMMARY.md "archive\old-docs\" 2>nul
    move /Y GITHUB_SETUP.md "archive\old-docs\" 2>nul
    move /Y REPOSITORY_GUIDE.md "archive\old-docs\" 2>nul
    
    REM Move development/analysis files
    echo Moving development files...
    move /Y ANALYSIS*.md "archive\old-docs\" 2>nul
    move /Y BINDINGS*.md "archive\old-docs\" 2>nul
    move /Y CPP*.md "archive\old-docs\" 2>nul
    move /Y DEPLOYMENT*.md "archive\old-docs\" 2>nul
    move /Y HOW_TO*.md "archive\old-docs\" 2>nul
    move /Y IMPLEMENTATION*.md "archive\old-docs\" 2>nul
    move /Y JARVIS_*.md "archive\old-docs\" 2>nul
    move /Y NEO*.md "archive\old-docs\" 2>nul
    move /Y PACKAGING*.md "archive\old-docs\" 2>nul
    move /Y QUICK_START.md "archive\old-docs\" 2>nul
    move /Y START_HERE.md "archive\old-docs\" 2>nul
    move /Y WHATS_WORKING.md "archive\old-docs\" 2>nul
    
    REM Move helper scripts to archive (keep only main ones)
    echo Moving old scripts...
    move /Y DEMO_JARVIS.bat "archive\" 2>nul
    move /Y JARVIS_NEO.bat "archive\" 2>nul
    move /Y HOW_TO_USE_JARVIS.bat "archive\" 2>nul
    move /Y RUN_VAD.bat "archive\" 2>nul
    move /Y test_jarvis_interactive.bat "archive\" 2>nul
    move /Y test_vad.bat "archive\" 2>nul
    
    REM Keep essential batch files, move others
    move /Y run_jarvis.bat "archive\" 2>nul
    move /Y run_tests.bat "archive\" 2>nul
    move /Y install.bat "archive\" 2>nul
    move /Y uninstall.bat "archive\" 2>nul
    
    REM Delete cleanup scripts (no longer needed)
    del /Q CLEANUP_OLD_DOCS.bat 2>nul
    
    echo.
    echo ==================================================================
    echo  CLEANUP COMPLETE!
    echo ==================================================================
    echo.
    echo  Root directory is now CLEAN and PROFESSIONAL!
    echo.
    echo  Essential files in root:
    echo     - README.md
    echo     - LICENSE
    echo     - requirements.txt
    echo     - START_JARVIS.bat
    echo     - jarvis_simple_working.py
    echo     - simple_tts.py
    echo     - CHECK_EVERYTHING.py
    echo     - docs/ (organized documentation)
    echo     - core/ (source code)
    echo.
    echo  Old files archived in:
    echo     - archive/sprints/
    echo     - archive/old-docs/
    echo     - archive/test-results/
    echo     - archive/old-status/
    echo.
    echo  Next: Run SHOW_SUMMARY.bat to see clean structure
    echo.
) else (
    echo.
    echo  Cleanup cancelled.
    echo.
)

echo ==================================================================
echo.
pause

