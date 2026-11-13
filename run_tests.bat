@echo off
echo ========================================================
echo Running YottaFlex Automated Test Suite (22 Tests)...
echo ========================================================
if exist .venv\Scripts\python.exe (
    .\.venv\Scripts\python.exe -m pytest backend/tests -v
) else (
    pytest backend/tests -v
)
pause
