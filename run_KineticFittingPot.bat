@echo off
setlocal
cd /d "%~dp0"
if not exist .venv\Scripts\streamlit.exe (
  call setup_KineticFittingPot.bat
  if errorlevel 1 exit /b 1
)
set KINETICFITTINGPOT_MODE=local
.venv\Scripts\python.exe -m streamlit run app.py --server.headless false
