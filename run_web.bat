@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting Web Dashboard...
python app.py
pause