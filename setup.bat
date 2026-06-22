@echo off
REM ===========================================================================
REM setup.bat
REM ---------
REM One-click setup for Windows. Double-click this file in File Explorer,
REM or run it from PowerShell/cmd with:  .\setup.bat
REM
REM What it does, step by step:
REM   1. Creates a Python virtual environment in .venv (if not already there)
REM   2. Activates it
REM   3. Installs all required packages from requirements.txt
REM   4. Creates your .env file from .env.example (if you don't have one yet)
REM
REM After this finishes, you still need to:
REM   - put your Bhagavad Gita PDF into the data\ folder
REM   - run: run_ingest.bat
REM   - then: run_app.bat
REM (No API key needs to go in .env — every user pastes their own key
REM  directly into the running app's sidebar.)
REM ===========================================================================

echo ============================================
echo  GitaVaani setup starting...
echo ============================================

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
) else (
    echo Virtual environment already exists, skipping creation.
)

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo Installing dependencies from requirements.txt...
echo (This may take a few minutes the first time - it downloads PyTorch too)
pip install -r requirements.txt

if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
) else (
    echo .env file already exists, leaving it untouched.
)

echo.
echo ============================================
echo  Setup complete!
echo  Next steps:
echo    1. Put your Bhagavad Gita PDF in the data\ folder
echo    2. Run: run_ingest.bat
echo    3. Run: run_app.bat
echo    4. Paste your own free Gemini API key into the
echo       app's sidebar when it opens (get one at
echo       aistudio.google.com)
echo ============================================
pause
