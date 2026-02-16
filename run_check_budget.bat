@echo off
REM Script pour vérifier les dépassements de budget
REM À exécuter quotidiennement via le Planificateur de tâches Windows

echo ========================================
echo Verification des budgets
echo ========================================
echo.

cd /d "%~dp0"
python manage.py check_budget

echo.
echo ========================================
echo Verification terminee
echo ========================================
pause
