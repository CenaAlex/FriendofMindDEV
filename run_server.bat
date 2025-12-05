@echo off
echo ========================================
echo   FriendOfMind - Starting Server
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Could not activate virtual environment!
    echo Make sure venv folder exists.
    pause
    exit /b 1
)

echo [2/3] Checking Django installation...
python -m django --version
if errorlevel 1 (
    echo ERROR: Django not found! Installing...
    pip install Django==4.2.* pillow
)

echo [3/3] Starting development server...
echo.
echo ========================================
echo   Server starting at http://127.0.0.1:8000/
echo   Press CTRL+C to stop the server
echo ========================================
echo.

python manage.py runserver

pause

