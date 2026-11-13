@echo off
echo ========================================================
echo Pushing YottaFlex Application to GitHub...
echo Repository: https://github.com/jadhavkrishnachaitanya/employee-lifecycle-automation-platform
echo ========================================================
git push -u --force origin main
if %ERRORLEVEL% equ 0 (
    echo ========================================================
    echo SUCCESS! Application successfully uploaded to GitHub:
    echo https://github.com/jadhavkrishnachaitanya/employee-lifecycle-automation-platform
    echo ========================================================
) else (
    echo ========================================================
    echo Push failed. Please check your GitHub permissions or sign in.
    echo ========================================================
)
pause
