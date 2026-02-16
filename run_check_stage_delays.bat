@echo off
REM Script pour vérifier les retards d'étapes
REM À exécuter quotidiennement via le Planificateur de tâches Windows

echo ========================================
echo Verification des retards d'etapes
echo ========================================
echo.

cd /d "%~dp0"
python manage.py check_stage_delays

echo.
echo ========================================
echo Verification terminee
echo ========================================
pause
