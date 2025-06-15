@echo off
echo ========================================
echo =      AIRFLOW DOCKER - DEMARRAGE      =
echo ========================================
echo.

REM Vérifier si Docker est en cours d'exécution
docker info > NUL 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Docker n'est pas en cours d'execution. Veuillez demarrer Docker Desktop.
    pause
    exit /b 1
)

REM Arrêter les conteneurs existants
echo [INFO] Arret des conteneurs Docker existants...
docker-compose down -v 2>NUL
docker rm -f airflow-postgres airflow-webserver airflow-scheduler 2>NUL

REM Nettoyer les volumes
echo.
echo [INFO] Nettoyage des volumes...
docker volume rm airflow_postgres-db-volume 2>NUL

REM Créer les dossiers essentiels
echo.
echo [INFO] Verification des dossiers essentiels...
if not exist dags mkdir dags
if not exist logs mkdir logs
if not exist plugins mkdir plugins
if not exist data mkdir data
if not exist scripts mkdir scripts

REM Démarrer les conteneurs
echo.
echo [INFO] Demarrage des conteneurs Airflow...
docker-compose up -d

REM Attendre que les conteneurs démarrent
echo.
echo [INFO] Demarrage en cours...
timeout /t 10 /nobreak > NUL

REM Vérifier l'état des conteneurs
echo.
echo [INFO] Verification de l'etat des conteneurs...
docker ps --filter "name=airflow"

echo.
echo ========================================
echo =         ACCES A L'INTERFACE WEB      =
echo ========================================
echo URL: http://localhost:8080
echo Identifiants: admin / admin
echo.
echo Pour verifier l'etat des conteneurs: docker ps
echo Pour voir les logs: docker logs airflow-webserver
echo Pour arreter: docker-compose down
echo.
pause
