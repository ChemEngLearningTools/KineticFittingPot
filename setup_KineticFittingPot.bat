@echo off
setlocal
cd /d "%~dp0"
echo ========================================
echo  KineticFittingPot - local setup
echo ========================================
where py >nul 2>nul
if %errorlevel%==0 (
  set PYTHON=py -3.12
) else (
  set PYTHON=python
)
if not exist .venv\Scripts\python.exe (
  echo Creating Python virtual environment...
  %PYTHON% -m venv .venv || goto :error
)
echo Installing/updating pinned requirements...
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt || goto :error
echo.
echo Setup complete.
exit /b 0
:error
echo.
echo Setup failed. Review the messages above.
pause
exit /b 1
