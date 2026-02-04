@echo off
REM QAI Models Setup Batch Script
REM ===============================

setlocal enabledelayedexpansion

cd /d "%~dp0"

echo.
echo ================================================================
echo  QAI MODELS SETUP
echo ================================================================

REM Check if venv exists
if not exist "venv\Scripts\python.exe" (
    echo.
    echo ERROR: Virtual environment not found at venv\Scripts\python.exe
    echo Please run: python -m venv venv
    exit /b 1
)

echo.
echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [2/3] Verifying dependencies...
python -c "import qiskit; import pennylane; import torch; print('All dependencies OK')" || (
    echo.
    echo WARNING: Some dependencies missing. Installing...
    pip install -q qiskit pennylane torch
)

echo.
echo [3/3] Running setup script...
python setup_qai_models.py

echo.
echo ================================================================
echo  SETUP COMPLETE
echo ================================================================
echo.
echo Next steps:
echo   1. Start dashboard: start_dashboard.sh
echo   2. Run training:    python examples\train_models.py
echo   3. Test locally:    python examples\run_simulations.py
echo.

pause
