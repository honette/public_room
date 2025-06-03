@echo off

if not exist venv (
  echo Creating virtual environment...
  python -m venv venv
)

echo Installing Flask...
venv\Scripts\pip install flask >nul

echo Launching app at http://localhost:5001 ...
venv\Scripts\python list.py
