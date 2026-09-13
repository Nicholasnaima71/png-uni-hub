@echo off
title PNG Uni Hub - Starting System
cd /d "%~dp0"

echo ================================
echo   PNG Uni Hub - Starting System
echo ================================
echo.

REM Check if app.py exists in the current folder
if exist "app.py" goto :found_app

REM Check one level deeper (in case of nested folder)
if exist "PNG-University-Guide\app.py" (
    cd PNG-University-Guide
    goto :found_app
)

echo ERROR: app.py not found!
echo Make sure run.bat is placed in the same folder as app.py
pause
exit /b

:found_app
echo Found app.py - OK
echo.

REM Try to find a working Python
where python >nul 2>nul
if %errorlevel% == 0 (
    python -c "import flask" >nul 2>nul
    if %errorlevel% == 0 (
        echo Using Python from PATH
        python app.py
        goto :end
    )
)

REM Try common Python install locations
for %%P in (
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python312\python.exe"
    "C:\Users\%USERNAME%\AppData\Local\Programs\Python\Python313\python.exe"
    "C:\Program Files\Python312\python.exe"
    "C:\Program Files\Python313\python.exe"
) do (
    if exist %%P (
        echo Using Python at %%P
        %%P -m pip install flask flask-cors >nul 2>nul
        %%P app.py
        goto :end
    )
)

echo ERROR: Python not found!
echo Please install Python 3.12.10 from https://www.python.org/downloads/
pause

:end
pause
