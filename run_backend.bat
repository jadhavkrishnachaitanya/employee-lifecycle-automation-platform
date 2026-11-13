@echo off
echo ========================================================
echo Starting YottaFlex Backend API Server...
echo ========================================================
if exist .venv\Scripts\python.exe (
    .\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
) else (
    python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
)
pause
