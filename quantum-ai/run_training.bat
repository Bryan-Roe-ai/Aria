@echo off
REM Run QAI Training Examples
REM ===========================

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ================================================================
echo  QUANTUM AI TRAINING - MODELS EXAMPLE
echo ================================================================
echo.

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found
    echo Please ensure quantum-ai/venv is set up
    exit /b 1
)

REM Activate venv and run training
echo [INFO] Activating quantum-ai environment...
call venv\Scripts\activate.bat

echo.
echo [INFO] Starting training...
python examples\train_models.py

echo.
echo ================================================================
echo  TRAINING COMPLETE
echo ================================================================
echo.
echo Results saved to: results/
echo.

pause
