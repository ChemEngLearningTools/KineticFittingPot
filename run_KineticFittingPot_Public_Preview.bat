@echo off
setlocal
cd /d "%~dp0"
set "KINETICFITTINGPOT_MODE=public_cloud"
echo PUBLIC MODE PREVIEW: Advanced Diagnostics should be locked.
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m streamlit run app.py
) else (
    py -m streamlit run app.py
    if errorlevel 9009 python -m streamlit run app.py
)
pause
