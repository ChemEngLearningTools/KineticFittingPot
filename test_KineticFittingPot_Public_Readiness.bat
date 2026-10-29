@echo off
setlocal
cd /d "%~dp0"
echo KineticFittingPot v1.14 - Validation and benchmarking
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" tools\public_readiness_v114.py %*
) else (
    py tools\public_readiness_v114.py %*
    if errorlevel 9009 python tools\public_readiness_v114.py %*
)
echo.
echo Reports: validation_reports\KineticFittingPot_v1_14_results.md
pause
