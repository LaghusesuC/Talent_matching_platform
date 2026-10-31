@echo off
cd /d "%~dp0"
echo Starting Resume Screening Platform Backend with Python 3.11...
set "PYTHONPATH=.;venv\Lib\site-packages"
"C:\Users\laghu\AppData\Local\Programs\Python\Python311\python.exe" -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
pause

