@echo off
REM ============================================================================
REM DEPLOIEMENT - SI-GOUVERNANCE
REM ============================================================================
REM Script unifie pour deploiement local et production
REM ============================================================================

echo.
echo ============================================================================
echo   DEPLOIEMENT SI-GOUVERNANCE
echo ============================================================================
echo.

REM Verifier Docker
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Docker n'est pas installe!
    pause
    exit /b 1
)

docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo [ERREUR] Docker Compose n'est pas installe!
    pause
    exit /b 1
)

REM Menu principal
echo Choisissez le mode de deploiement:
echo.
echo   MODE LOCAL (Developpement)
echo   1. Deploiement complet local (premiere fois)
echo   2. Demarrage local
echo   3. Local avec monitoring (Flower)
echo.
echo   MODE PRODUCTION
echo   4. Deploiement production
echo   5. Production avec monitoring
echo.
echo   AUTRES
echo   6. Arreter tous les services
echo   7. Voir les logs
echo   8. Nettoyer tout
echo.
set /p choice="Votre choix (1-8): "

if "%choice%"=="1" goto deploy_local_full
if "%choice%"=="2" goto start_local
if "%choice%"=="3" goto start_local_monitoring
if "%choice%"=="4" goto deploy_production
if "%choice%"=="5" goto deploy_production_monitoring
if "%choice%"=="6" goto stop
if "%choice%"=="7" goto logs
if "%choice%"=="8" goto clean
echo Choix invalide!
pause
exit /b 1

:deploy_local_full
echo.
echo ============================================================================
echo   DEPLOIEMENT LOCAL COMPLET
echo ============================================================================
echo.
if not exist .env (
    echo [INFO] Creation du fichier .env...
    copy .env.example .env
)
echo [INFO] Arret des services existants...
docker-compose down
echo [INFO] Build des images...
docker-compose build
echo [INFO] Demarrage des services...
docker-compose up -d
echo [INFO] Attente du demarrage (30 secondes)...
timeout /t 30 /nobreak >nul
docker-compose ps
goto success_local

:start_local
echo.
echo [INFO] Demarrage local...
if not exist .env (
    copy .env.example .env
)
docker-compose up -d
timeout /t 15 /nobreak >nul
docker-compose ps
goto success_local

:start_local_monitoring
echo.
echo [INFO] Demarrage local avec monitoring...
if not exist .env (
    copy .env.example .env
)
docker-compose --profile monitoring up -d
timeout /t 15 /nobreak >nul
docker-compose ps
goto success_local_monitoring

:deploy_production
echo.
echo ============================================================================
echo   DEPLOIEMENT PRODUCTION
echo ============================================================================
echo.
if not exist .env.production (
    echo [ERREUR] Fichier .env.production manquant!
    echo Copiez .env.production.example vers .env.production
    echo et configurez les valeurs de production.
    pause
    exit /b 1
)
echo [INFO] Arret des services existants...
docker-compose down
echo [INFO] Build des images production...
docker-compose --profile production build
echo [INFO] Demarrage en mode production...
docker-compose --profile production up -d
echo [INFO] Attente du demarrage (30 secondes)...
timeout /t 30 /nobreak >nul
docker-compose ps
goto success_production

:deploy_production_monitoring
echo.
echo [INFO] Demarrage production avec monitoring...
if not exist .env.production (
    echo [ERREUR] Fichier .env.production manquant!
    pause
    exit /b 1
)
docker-compose --profile production --profile monitoring up -d
timeout /t 15 /nobreak >nul
docker-compose ps
goto success_production_monitoring

:stop
echo.
echo [INFO] Arret de tous les services...
docker-compose down
docker-compose --profile production down
docker-compose --profile monitoring down
echo [OK] Services arretes
pause
exit /b 0

:logs
echo.
echo [INFO] Logs (Ctrl+C pour quitter)...
docker-compose logs -f
exit /b 0

:clean
echo.
echo [ATTENTION] Cela va supprimer TOUTES les donnees!
set /p confirm="Taper 'OUI' pour confirmer: "
if not "%confirm%"=="OUI" (
    echo Annule
    pause
    exit /b 0
)
docker-compose down -v
docker-compose --profile production down -v
docker system prune -f
echo [OK] Nettoyage termine
pause
exit /b 0

:success_local
echo.
echo ============================================================================
echo   DEPLOIEMENT LOCAL REUSSI!
echo ============================================================================
echo.
echo Services disponibles:
echo   - Application:  http://localhost:8000
echo   - Base donnees: localhost:3306
echo   - Redis:        localhost:6379
echo.
echo Superutilisateur cree automatiquement:
echo   - Username: jovi
echo   - Password: jovi123
echo.
echo Commandes utiles:
echo   - Logs:     docker-compose logs -f
echo   - Arreter:  docker-compose down
echo   - Shell:    docker-compose exec web python manage.py shell
echo.
pause
exit /b 0

:success_local_monitoring
echo.
echo ============================================================================
echo   DEPLOIEMENT LOCAL + MONITORING REUSSI!
echo ============================================================================
echo.
echo Services disponibles:
echo   - Application:  http://localhost:8000
echo   - Flower:       http://localhost:5555
echo   - Base donnees: localhost:3306
echo   - Redis:        localhost:6379
echo.
echo Superutilisateur: jovi / jovi123
echo.
pause
exit /b 0

:success_production
echo.
echo ============================================================================
echo   DEPLOIEMENT PRODUCTION REUSSI!
echo ============================================================================
echo.
echo Services disponibles:
echo   - Application:  http://localhost (via Nginx)
echo   - HTTPS:        https://localhost (si configure)
echo.
echo IMPORTANT:
echo   - Configurez votre domaine dans Nginx
echo   - Configurez les certificats SSL
echo   - Verifiez les logs: docker-compose --profile production logs -f
echo.
pause
exit /b 0

:success_production_monitoring
echo.
echo ============================================================================
echo   DEPLOIEMENT PRODUCTION + MONITORING REUSSI!
echo ============================================================================
echo.
echo Services disponibles:
echo   - Application:  http://localhost (via Nginx)
echo   - Flower:       http://localhost:5555 (interne uniquement)
echo.
echo ATTENTION: Flower ne doit PAS etre expose publiquement!
echo.
pause
exit /b 0
