@echo off
setlocal
cd /d "%~dp0"
echo KineticFittingPot v1.17 - Final technical validation
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" tools\deployment_readiness_v117.py %*
) else (
    py tools\deployment_readiness_v117.py %*
    if errorlevel 9009 python tools\deployment_readiness_v117.py %*
)
echo.
echo Report: validation_reports\KineticFittingPot_v1_17_results.md
pause
