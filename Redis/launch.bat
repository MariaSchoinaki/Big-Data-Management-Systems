@echo off
echo ==============================
echo Launching Redis Meeting App
echo ==============================

:: Navigate to the project folder (optional if already inside)
cd /d %~dp0

:: Activate the virtual environment
echo Activating virtual environment...
call .venv\Scripts\activate.bat

:: Run the launch_app.py script
echo Starting launch_app.py...
python launch_app.py

:: After GUI closes, virtual environment deactivates automatically when the cmd window closes