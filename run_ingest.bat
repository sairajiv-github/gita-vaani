@echo off
REM ===========================================================================
REM run_ingest.bat
REM --------------
REM One-click script to build the FAISS vector index. Run this ONCE after
REM adding your Bhagavad Gita PDF to the data\ folder, and again any time
REM you change that file.
REM ===========================================================================

call .venv\Scripts\activate.bat
python ingest.py
pause
