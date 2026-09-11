@echo off
cd /d "%~dp0"

echo ================================
echo   PNG Uni Hub - Starting System
echo ================================
echo.

REM Try the new stable Python first (for this PC)
if exist "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" (
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe" app.py
    goto :end
)

REM Try Python from PATH (for other computers)
where python >nul 2>nul
if %errorlevel% == 0 (
    python app.py
    goto :end
)

echo Python not found! Please install Python 3.12.10.
pause

:end
pause