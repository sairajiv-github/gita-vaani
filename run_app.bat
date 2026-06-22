@echo off
REM ===========================================================================
REM run_app.bat
REM -----------
REM One-click script to start the GitaVaani chatbot. Run this any time you
REM want to use the app (after setup.bat and run_ingest.bat have already
REM been run at least once).
REM ===========================================================================

call .venv\Scripts\activate.bat
streamlit run app.py
pause
