@echo off
setlocal EnableDelayedExpansion
title Tree Plantation - One-Click Setup
color 0A

echo.
echo ============================================================
echo    Tree Plantation Data Collection - Setup
echo ============================================================
echo.

REM Step 1: Check Python
echo [1/5] Checking Python...
where python >nul 2>nul
if errorlevel 1 (
    echo ERROR: Python not found.
    echo Please install Python 3.10+ from https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
for /f "tokens=2" %%v in ('python --version 2^>^&1') do set PYVER=%%v
echo OK - Python !PYVER! found
echo.

REM Step 2: Create venv
echo [2/5] Creating virtual environment...
if exist "venv\" (
    echo venv already exists - reusing
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create venv
        pause
        exit /b 1
    )
)
call venv\Scripts\activate.bat
echo OK - venv activated
echo.

REM Step 3: Upgrade pip
echo [3/5] Upgrading pip...
python -m pip install --upgrade pip --quiet
echo OK
echo.

REM Step 4: Install dependencies
echo [4/5] Installing packages (may take a few minutes)...
if exist "requirements.txt" (
    python -m pip install -r requirements.txt
) else (
    python -m pip install streamlit pandas supabase Pillow openpyxl python-dotenv
)
if errorlevel 1 (
    echo ERROR: Package installation failed.
    pause
    exit /b 1
)
echo OK - All packages installed
echo.

REM Step 5: Secrets
echo [5/5] Supabase configuration...
if not exist ".streamlit" mkdir .streamlit
set "SECRETS_FILE=.streamlit\secrets.toml"

if exist "%SECRETS_FILE%" (
    echo secrets.toml already exists - skipping configuration
    goto :run_app
)

echo.
echo Enter your Supabase project details:
echo (Find them at: Project Settings - API)
echo.
set /p SUPABASE_URL="Supabase URL (e.g. https://xxx.supabase.co): "
set /p SUPABASE_KEY="Supabase anon key: "
set /p ADMIN_PASS="Admin password (optional, press Enter for 'admin123'): "
if "!ADMIN_PASS!"=="" set "ADMIN_PASS=admin123"

(
    echo [supabase]
    echo url = "!SUPABASE_URL!"
    echo key = "!SUPABASE_KEY!"
    echo.
    echo [admin]
    echo password = "!ADMIN_PASS!"
) > "%SECRETS_FILE%"
echo OK - secrets.toml created
echo.

:run_app
echo Starting Streamlit...
echo Browser will open at: http://localhost:8501
echo Press Ctrl+C to stop.
echo.
timeout /t 2 >nul
start "" http://localhost:8501
streamlit run streamlit_app.py

pause
endlocal