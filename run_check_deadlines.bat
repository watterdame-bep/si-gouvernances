@echo off
REM ============================================
REM Verification des alertes de projets
REM Executer quotidiennement via le Planificateur de taches Windows
REM ============================================

echo [%date% %time%] Debut verification alertes >> logs\alertes.log

REM Aller dans le repertoire du projet
cd /d "%~dp0"

REM Activer l'environnement virtuel si necessaire
REM Decommentez la ligne suivante si vous utilisez un venv
REM call venv\Scripts\activate.bat

REM Executer la commande de verification
python manage.py check_project_deadlines >> logs\alertes.log 2>&1

echo [%date% %time%] Fin verification alertes >> logs\alertes.log
echo. >> logs\alertes.log
