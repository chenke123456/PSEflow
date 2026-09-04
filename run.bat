@echo off
cd /d "%~dp0"
echo Starting CK Workflow...
python -c "import fastapi,uvicorn" 2>nul
if errorlevel 1 (
  echo Installing dependencies...
  python -m pip install -r requirements.txt
  if errorlevel 1 (
    echo pip install failed.
    pause
    exit /b 1
  )
)
python app.py --port 8787
if errorlevel 1 (
  echo.
  echo Start failed. Open http://127.0.0.1:8787
  pause
)
