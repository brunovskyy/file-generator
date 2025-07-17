@echo off
echo Building DocGenius with Console Window...
echo.

REM Try different Python commands
where python >nul 2>&1
if %errorlevel% == 0 (
    echo Using 'python'
    python -m PyInstaller --name DocGenius-Console --onefile --clean app_launcher_cli.py
    goto :done
)

where py >nul 2>&1
if %errorlevel% == 0 (
    echo Using 'py'
    py -m PyInstaller --name DocGenius-Console --onefile --clean app_launcher_cli.py
    goto :done
)

REM Try with full path if venv exists
if exist ".venv\Scripts\python.exe" (
    echo Using venv Python
    .venv\Scripts\python.exe -m PyInstaller --name DocGenius-Console --onefile --clean app_launcher_cli.py
    goto :done
)

echo ERROR: Python not found! Please install Python or activate virtual environment.
pause
exit /b 1

:done
echo.
echo Build complete! Check dist\DocGenius-Console.exe
echo This version will show a console window when you run it.
pause
