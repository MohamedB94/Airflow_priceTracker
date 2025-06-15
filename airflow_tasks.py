#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Utilitaire pour les tâches Airflow - Interface simplifiée pour gérer les DAGs et les tâches

Ce script fournit une interface utilisateur simple pour gérer les tâches Airflow
sans avoir à utiliser la ligne de commande ou l'interface web.
"""

import os
import sys
import subprocess
import time
import logging
import datetime
import webbrowser
from pathlib import Path

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('airflow_tasks')

# Constantes
AIRFLOW_DIR = os.path.dirname(os.path.abspath(__file__))
DOCKER_COMPOSE_FILE = os.path.join(AIRFLOW_DIR, 'docker-compose.yml')
DAGS_FOLDER = os.path.join(AIRFLOW_DIR, 'dags')
AIRFLOW_UI_URL = "http://localhost:8080"

def print_header(title):
    """Affiche un titre formaté"""
    print("\n" + "=" * 60)
    print(f" {title} ".center(60, '='))
    print("=" * 60 + "\n")

def print_menu():
    """Affiche le menu principal"""
    print_header("GESTIONNAIRE DE TÂCHES AIRFLOW")
    print("1. Démarrer Airflow avec Docker")
    print("2. Arrêter Airflow")
    print("3. Vérifier l'état des conteneurs Airflow")
    print("4. Ouvrir l'interface web Airflow")
    print("5. Lister les DAGs disponibles")
    print("6. Vérifier les logs")
    print("7. Réinitialiser l'environnement Airflow")
    print("8. Aide et documentation")
    print("0. Quitter")
    print("\n")

def run_command(command, shell=True):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(
            command, 
            shell=shell, 
            check=True,
            capture_output=True,
            text=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Erreur lors de l'exécution de la commande: {e}")
        logger.error(f"Sortie d'erreur: {e.stderr}")
        return None

def start_airflow():
    """Démarre Airflow avec Docker"""
    print("Démarrage d'Airflow avec Docker...")
    
    # Vérifie si Docker est en cours d'exécution
    if not run_command("docker info"):
        print("[ERREUR] Docker n'est pas en cours d'exécution. Veuillez démarrer Docker Desktop.")
        return False
    
    # Utilise le script bat si disponible, sinon exécute la commande directement
    bat_file = os.path.join(AIRFLOW_DIR, "airflow.bat")
    if os.path.exists(bat_file):
        run_command(bat_file)
    else:
        # Arrête les conteneurs existants
        run_command("docker-compose down -v")
        
        # Crée les dossiers nécessaires s'ils n'existent pas
        for folder in ['dags', 'logs', 'plugins', 'data', 'scripts']:
            os.makedirs(os.path.join(AIRFLOW_DIR, folder), exist_ok=True)
        
        # Démarre les conteneurs
        run_command("docker-compose up -d")
    
    # Vérifie si les conteneurs sont démarrés
    time.sleep(5)  # Attendre que les conteneurs démarrent
    containers = run_command("docker ps --filter 'name=airflow'")
    
    if containers and "airflow-webserver" in containers:
        print("[SUCCESS] Airflow a été démarré avec succès !")
        print(f"Interface web disponible sur: {AIRFLOW_UI_URL}")
        print("Identifiants: admin / admin")
        return True
    else:
        print("[ERREUR] Un problème est survenu lors du démarrage d'Airflow.")
        print("Consultez les logs pour plus d'informations.")
        return False

def stop_airflow():
    """Arrête Airflow"""
    print("Arrêt d'Airflow...")
    
    # Utilise le script bat si disponible, sinon exécute la commande directement
    bat_file = os.path.join(AIRFLOW_DIR, "airflow_stop.bat")
    if os.path.exists(bat_file):
        run_command(bat_file)
    else:
        run_command("docker-compose down")
    
    print("[SUCCESS] Airflow a été arrêté.")

def check_airflow_status():
    """Vérifie l'état des conteneurs Airflow"""
    print_header("ÉTAT DES CONTENEURS AIRFLOW")
    
    output = run_command("docker ps --filter 'name=airflow'")
    if output:
        print(output)
    else:
        print("Aucun conteneur Airflow n'est en cours d'exécution.")
    
    input("\nAppuyez sur Entrée pour continuer...")

def open_airflow_ui():
    """Ouvre l'interface web Airflow dans le navigateur par défaut"""
    print(f"Ouverture de l'interface web Airflow: {AIRFLOW_UI_URL}")
    webbrowser.open(AIRFLOW_UI_URL)

def list_dags():
    """Liste les DAGs disponibles"""
    print_header("DAGS DISPONIBLES")
    
    dags_folder = Path(DAGS_FOLDER)
    if not dags_folder.exists():
        print(f"[ERREUR] Le dossier DAGs n'existe pas: {DAGS_FOLDER}")
        return
    
    dag_files = list(dags_folder.glob("*.py"))
    
    if not dag_files:
        print("Aucun DAG trouvé dans le dossier dags/")
    else:
        print(f"Nombre de DAGs trouvés: {len(dag_files)}\n")
        for i, dag_file in enumerate(dag_files, 1):
            # Tente de lire l'ID du DAG à partir du fichier
            dag_id = "Inconnu"
            try:
                with open(dag_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    if "dag_id=" in content:
                        dag_id_line = [line for line in content.split('\n') if "dag_id=" in line]
                        if dag_id_line:
                            dag_id = dag_id_line[0].split("dag_id=")[1].strip().strip("'").strip('"').strip(',')
            except Exception as e:
                logger.error(f"Erreur lors de la lecture du fichier DAG {dag_file}: {e}")
            
            print(f"{i}. {dag_file.name} (ID: {dag_id})")
    
    input("\nAppuyez sur Entrée pour continuer...")

def check_logs():
    """Vérifie les logs des conteneurs Airflow"""
    print_header("LOGS AIRFLOW")
    
    containers = ["airflow-webserver", "airflow-scheduler", "airflow-postgres"]
    
    for container in containers:
        print(f"\n--- Logs récents de {container} ---\n")
        logs = run_command(f"docker logs --tail 20 {container}")
        if logs:
            print(logs)
        else:
            print(f"Impossible de récupérer les logs de {container}")
    
    input("\nAppuyez sur Entrée pour continuer...")

def reset_airflow():
    """Réinitialise l'environnement Airflow"""
    print_header("RÉINITIALISATION DE L'ENVIRONNEMENT AIRFLOW")
    
    print("Cette opération va arrêter tous les conteneurs Airflow, ")
    print("supprimer les volumes et réinitialiser la base de données.")
    confirmation = input("Êtes-vous sûr de vouloir continuer? (o/n): ")
    
    if confirmation.lower() != 'o':
        print("Opération annulée.")
        return
    
    print("\nRéinitialisation en cours...")
    
    # Arrête les conteneurs existants
    run_command("docker-compose down -v")
    
    # Supprime les volumes
    run_command("docker volume rm airflow_postgres-db-volume")
    
    # Supprime les fichiers de base de données SQLite
    for db_file in Path(AIRFLOW_DIR).glob("*.db"):
        try:
            db_file.unlink()
            print(f"Fichier supprimé: {db_file}")
        except Exception as e:
            logger.error(f"Erreur lors de la suppression de {db_file}: {e}")
    
    print("[SUCCESS] Réinitialisation terminée.")
    print("Vous pouvez maintenant redémarrer Airflow.")
    
    input("\nAppuyez sur Entrée pour continuer...")

def show_help():
    """Affiche l'aide et la documentation"""
    print_header("AIDE ET DOCUMENTATION")
    
    print("Airflow est un outil de gestion de flux de travail permettant de")
    print("planifier, exécuter et surveiller des processus automatisés.")
    print("\nCet utilitaire vous permet de gérer Airflow avec Docker facilement.")
    print("\nDocumentation:")
    print("- Documentation Airflow: https://airflow.apache.org/docs/")
    print("- Guide Docker: README.md dans le dossier du projet")
    print("\nStructure du projet:")
    print("- dags/: Contient les définitions de flux de travail (DAGs)")
    print("- scripts/: Scripts utilisés par les DAGs")
    print("- data/: Données utilisées ou générées par les DAGs")
    print("- logs/: Logs d'exécution d'Airflow")
    print("- plugins/: Extensions et plugins pour Airflow")
    
    input("\nAppuyez sur Entrée pour continuer...")

def main():
    """Fonction principale"""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_menu()
        
        choice = input("Entrez votre choix (0-8): ")
        
        if choice == '0':
            print("Au revoir!")
            sys.exit(0)
        elif choice == '1':
            start_airflow()
            input("\nAppuyez sur Entrée pour continuer...")
        elif choice == '2':
            stop_airflow()
            input("\nAppuyez sur Entrée pour continuer...")
        elif choice == '3':
            check_airflow_status()
        elif choice == '4':
            open_airflow_ui()
            input("\nAppuyez sur Entrée pour continuer...")
        elif choice == '5':
            list_dags()
        elif choice == '6':
            check_logs()
        elif choice == '7':
            reset_airflow()
        elif choice == '8':
            show_help()
        else:
            print("Choix invalide. Veuillez réessayer.")
            input("\nAppuyez sur Entrée pour continuer...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nOpération annulée par l'utilisateur.")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Erreur inattendue: {e}")
        print(f"\n[ERREUR] Une erreur inattendue s'est produite: {e}")
        sys.exit(1)
