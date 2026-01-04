@echo off
echo Installing dependencies...
pip install -r requirements.txt
echo.
echo Starting AI Time-Wasting Detector...
python main.py
pause