@echo off
setlocal enabledelayedexpansion

echo ====================================================================
echo  ProcessCompass: VTU 24CS51 SEPM Decision Support System
echo ====================================================================

if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Creating venv...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment. Please check Python installation.
        exit /b 1
    )
)

echo [INFO] Activating virtual environment...
call venv\Scripts\activate.bat

echo [INFO] Verifying requirements...
python -m pip install -r requirements.txt --quiet

echo [INFO] Launching ProcessCompass on http://localhost:8501 ...
streamlit run app.py

pause
