@echo off
REM Start QAI Web Dashboard
REM ========================

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ================================================================
echo  QUANTUM AI TRAINING DASHBOARD
echo ================================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Please ensure quantum-ai/venv is set up
    exit /b 1
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install Flask if needed
echo [INFO] Verifying dashboard dependencies...
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing Flask and dependencies...
    pip install -q flask flask-cors
)

echo.
echo [INFO] Starting web server on port 5000...
echo.
echo Dashboard URL: http://localhost:5000
echo.
echo Features:
echo   * Real-time training visualization
echo   * Interactive parameter tuning
echo   * Live loss/accuracy charts
echo   * Training session management
echo.
echo Press Ctrl+C to stop the server
echo.

python web_app.py

pause
