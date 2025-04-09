@echo off
echo Starting Maharashtra Lokadhikar Samiti Borrower Management System...

REM Check if Python is installed
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH!
    echo Please install Python 3.7 or higher from https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)

REM Check if this is the first run
if not exist "venv" (
    echo First-time setup detected. Running easy installer...
    echo.
    python easy_install.py
) else (
    REM Start the application with virtual environment
    if exist "venv\Scripts\activate.bat" (
        call venv\Scripts\activate.bat
        start "" http://localhost:5000
        python app.py
        call venv\Scripts\deactivate.bat
    ) else (
        REM Fall back to system Python if venv activation fails
        start "" http://localhost:5000
        python app.py
    )
)

pause