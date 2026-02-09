@echo off
REM Script pour exécuter la vérification des échéances des tâches
REM À planifier dans le Planificateur de tâches Windows

REM Se déplacer dans le répertoire du projet
cd /d E:\DOCERA\PROJETS\PYTHON\Django\SI-GOUVERNANCE

REM Créer le dossier logs s'il n'existe pas
if not exist logs mkdir logs

echo ========================================
echo Verification des echeances des taches
echo ========================================
echo.

REM Ajouter un séparateur dans le log
echo ======================================================================== >> logs\planificateur.log
echo [%date% %time%] Demarrage verification echeances >> logs\planificateur.log
echo ======================================================================== >> logs\planificateur.log

REM Activer l'environnement virtuel si nécessaire
REM call venv\Scripts\activate

REM Exécuter la commande Django et capturer la sortie
python manage.py check_task_deadlines >> logs\planificateur.log 2>&1

REM Vérifier le code de sortie
if %ERRORLEVEL% EQU 0 (
    echo [%date% %time%] Verification terminee avec succes >> logs\planificateur.log
    echo Verification terminee avec succes
) else (
    echo [%date% %time%] ERREUR: Code de sortie %ERRORLEVEL% >> logs\planificateur.log
    echo ERREUR: Code de sortie %ERRORLEVEL%
)

echo. >> logs\planificateur.log
echo.
echo ========================================
echo Verification terminee
echo ========================================

REM Garder la fenêtre ouverte pour voir les résultats (optionnel)
REM pause

