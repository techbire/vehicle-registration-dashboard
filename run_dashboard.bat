@echo off
REM Vehicle Registration Dashboard Launch Script
REM This script launches the Streamlit dashboard

echo Starting Vehicle Registration Dashboard...
echo.

REM Change to project directory
cd /d "%~dp0"

REM Activate virtual environment and run dashboard
.venv\Scripts\python.exe -m streamlit run src\dashboard\app.py --server.port=8501

pause
