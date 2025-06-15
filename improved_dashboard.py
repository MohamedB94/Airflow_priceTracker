import os
import sys
import subprocess
import webbrowser
import time
import signal

# Ajouter le répertoire parent au chemin Python
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

# Définition des chemins
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
DASHBOARD_SCRIPT = os.path.join(SCRIPTS_DIR, 'dashboard_improved.py')

def signal_handler(sig, frame):
    """Gère l'arrêt propre du processus lors de l'interruption clavier (Ctrl+C)"""
    print("\nArrêt du tableau de bord demandé par l'utilisateur...")
    if dashboard_process:
        dashboard_process.terminate()
    sys.exit(0)

# Enregistre le gestionnaire de signal pour Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

# Vérifie l'existence des données
prices_csv = os.path.join(BASE_DIR, 'data', 'prices.csv')
if not os.path.exists(prices_csv):
    print(f"ATTENTION: Le fichier de données {prices_csv} n'existe pas.")
    print("Le tableau de bord pourrait ne pas fonctionner correctement.")
    print("Exécutez d'abord le scraper pour collecter des données de prix.")
    response = input("Voulez-vous continuer quand même? (o/n): ")
    if response.lower() != 'o':
        sys.exit(0)

# Vérifier les dépendances
try:
    import dash
    import plotly
    import pandas as pd
except ImportError as e:
    print(f"ERREUR: Dépendances manquantes - {str(e)}")
    print("Installez les dépendances requises avec:")
    print("pip install dash plotly pandas")
    sys.exit(1)

print("\n" + "="*60)
print(" DÉMARRAGE DU TABLEAU DE BORD DE SUIVI DES PRIX ".center(60, "="))
print("="*60 + "\n")

print("Initialisation du tableau de bord...")
dashboard_process = subprocess.Popen(
    [sys.executable, DASHBOARD_SCRIPT],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    text=True,
    bufsize=1,
    universal_newlines=True
)

# Attend que le serveur démarre
print("Démarrage du serveur en cours (cela peut prendre quelques instants)...")
time.sleep(3)

# Ouvre le navigateur
print("Ouverture du tableau de bord dans le navigateur...")
webbrowser.open('http://localhost:8050')

print("\nTableau de bord accessible à l'adresse: http://localhost:8050")
print("Gardez cette fenêtre ouverte tant que vous utilisez le tableau de bord.")
print("Appuyez sur Ctrl+C pour arrêter le tableau de bord quand vous avez terminé.\n")

# Surveille et affiche les sorties du processus
while True:
    try:
        # Vérifie si le processus est toujours actif
        if dashboard_process.poll() is not None:
            exit_code = dashboard_process.poll()
            error_output = dashboard_process.stderr.read()
            print(f"ERREUR: Le tableau de bord s'est arrêté avec le code {exit_code}")
            if error_output:
                print("Message d'erreur:")
                print(error_output)
            break
            
        # Lit les sorties standard et d'erreur sans bloquer
        output = dashboard_process.stdout.readline()
        if output:
            print(f"LOG: {output.strip()}")
            
        error = dashboard_process.stderr.readline()
        if error:
            print(f"ERREUR: {error.strip()}")
            
        time.sleep(0.1)
        
    except KeyboardInterrupt:
        print("\nArrêt du tableau de bord demandé par l'utilisateur...")
        dashboard_process.terminate()
        break
    except Exception as e:
        print(f"Exception inattendue: {str(e)}")
        dashboard_process.terminate()
        break

print("Tableau de bord arrêté.")
