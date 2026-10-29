@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\python.exe (
  call setup_KineticFittingPot.bat
  if errorlevel 1 exit /b 1
)
set KINETICFITTINGPOT_MODE=local
echo Compiling Python files...
.venv\Scripts\python.exe -m compileall -q app.py modules utils tools || goto :error
echo Running general batch model regression...
.venv\Scripts\python.exe tools\smoke_test_general_batch_model.py || goto :error
echo Running kinetic fitting engine regression...
.venv\Scripts\python.exe tools\smoke_test_kinetic_fitting_engine.py || goto :error
echo Running model diagnostics engine regression...
.venv\Scripts\python.exe tools\smoke_test_model_diagnostics_engine.py || goto :error
echo.
echo Core KineticFittingPot tests passed.
pause
exit /b 0
:error
echo.
echo A KineticFittingPot test FAILED.
pause
exit /b 1
