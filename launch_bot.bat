@echo off
cd /d "%~dp0"

REM Activate virtual environment
call venv\Scripts\activate

REM Run the automation script
python run_all.py

pause
