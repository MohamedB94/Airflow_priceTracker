@echo off
ECHO Arrêt des conteneurs Airflow s'ils sont en cours d'exécution...
docker compose down

ECHO Suppression des volumes pour reconstruction complète...
docker volume rm airflow_postgres-db-volume

ECHO Reconstruction des images Docker...
docker compose build

ECHO Démarrage des services Airflow...
docker compose up -d

ECHO Vérification des journaux du conteneur webserver...
ECHO Pour suivre les journaux en direct: docker logs -f airflow-webserver
TIMEOUT /T 10
docker logs airflow-webserver

ECHO ---------------------------------------
ECHO L'interface Airflow est accessible à: http://localhost:8080
ECHO Identifiants: admin / admin
ECHO ---------------------------------------
