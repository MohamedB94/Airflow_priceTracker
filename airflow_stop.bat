@echo off
echo ========================================
echo =      AIRFLOW DOCKER - ARRET          =
echo ========================================
echo.

echo [INFO] Arret des conteneurs Docker Airflow...
docker-compose down

echo.
echo [SUCCESS] Les conteneurs Airflow ont ete arretes.
echo.
pause
