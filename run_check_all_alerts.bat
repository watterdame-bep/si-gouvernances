@echo off
REM ============================================
REM Verification de TOUTES les alertes
REM - Alertes projets (echeances et retards)
REM - Alertes taches (retards)
REM - Alertes contrats (expirations)
REM Executer quotidiennement via le Planificateur de taches Windows
REM ============================================

echo ============================================
echo Verification de toutes les alertes
echo Date: %date% %time%
echo ============================================

REM Aller dans le repertoire du projet
cd /d "%~dp0"

REM Activer l'environnement virtuel si necessaire
REM Decommentez la ligne suivante si vous utilisez un venv
REM call venv\Scripts\activate.bat

REM Creer le dossier logs s'il n'existe pas
if not exist logs mkdir logs

echo.
echo [%date% %time%] === DEBUT VERIFICATION ALERTES === >> logs\alertes.log
echo.

REM 1. Verification des alertes de projets (echeances et retards)
echo [1/3] Verification des alertes de projets...
echo [%date% %time%] --- Verification alertes projets --- >> logs\alertes.log
python manage.py check_project_deadlines >> logs\alertes.log 2>&1
if %errorlevel% neq 0 (
    echo ERREUR lors de la verification des alertes de projets
    echo [%date% %time%] ERREUR check_project_deadlines >> logs\alertes.log
) else (
    echo OK - Alertes de projets verifiees
)

echo.

REM 2. Verification des alertes de taches (retards)
echo [2/3] Verification des alertes de taches...
echo [%date% %time%] --- Verification alertes taches --- >> logs\alertes.log
python manage.py check_task_deadlines >> logs\alertes.log 2>&1
if %errorlevel% neq 0 (
    echo ERREUR lors de la verification des alertes de taches
    echo [%date% %time%] ERREUR check_task_deadlines >> logs\alertes.log
) else (
    echo OK - Alertes de taches verifiees
)

echo.

REM 3. Verification des alertes de contrats (expirations)
echo [3/3] Verification des alertes de contrats...
echo [%date% %time%] --- Verification alertes contrats --- >> logs\alertes.log
python manage.py check_contract_expiration >> logs\alertes.log 2>&1
if %errorlevel% neq 0 (
    echo ERREUR lors de la verification des alertes de contrats
    echo [%date% %time%] ERREUR check_contract_expiration >> logs\alertes.log
) else (
    echo OK - Alertes de contrats verifiees
)

echo.
echo [%date% %time%] === FIN VERIFICATION ALERTES === >> logs\alertes.log
echo. >> logs\alertes.log

echo.
echo ============================================
echo Verification terminee
echo Consultez logs\alertes.log pour les details
echo ============================================

pause
