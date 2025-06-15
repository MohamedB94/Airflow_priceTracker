import os
import sys
import subprocess
import webbrowser
from time import sleep

# Ajout du répertoire parent au chemin
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Définition des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
DASHBOARD_SCRIPT = os.path.join(SCRIPTS_DIR, 'dashboard.py')

def start_dashboard():
    """Démarre le tableau de bord et l'ouvre dans un navigateur web"""
    print("Démarrage du Tableau de Bord de Suivi des Prix E-Commerce...")
    
    # Démarre le tableau de bord dans un processus séparé
    dashboard_process = subprocess.Popen(
        [sys.executable, DASHBOARD_SCRIPT],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Attend un moment pour que le tableau de bord démarre
    sleep(3)
    
    # Ouvre le tableau de bord dans le navigateur web par défaut
    webbrowser.open('http://localhost:8050')
    
    print("Tableau de bord démarré à http://localhost:8050")
    print("Appuyez sur Ctrl+C pour arrêter le tableau de bord")
    
    try:
        # Surveille le processus du tableau de bord
        while dashboard_process.poll() is None:
            output = dashboard_process.stdout.readline()
            if output:
                print(output.strip())
    except KeyboardInterrupt:
        print("Arrêt du tableau de bord...")
        dashboard_process.terminate()
        
    print("Tableau de bord arrêté")

if __name__ == "__main__":
    start_dashboard()
