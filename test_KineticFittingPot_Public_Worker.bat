@echo off
setlocal
cd /d "%~dp0"
set "KINETICFITTINGPOT_MODE=public_cloud"
if exist ".venv\Scripts\python.exe" (
  ".venv\Scripts\python.exe" -m tools.test_public_worker_v116
) else (
  py -m tools.test_public_worker_v116
  if errorlevel 9009 python -m tools.test_public_worker_v116
)
echo.
pause
