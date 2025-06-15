#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import json
import shutil
import subprocess
import webbrowser
import time
from datetime import datetime

# Définition des chemins
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')
DATA_DIR = os.path.join(BASE_DIR, 'data')
PRODUCTS_JSON = os.path.join(DATA_DIR, 'products.json')
VENV_DIR = os.path.join(BASE_DIR, 'airflow_env')
VENV_PYTHON = os.path.join(VENV_DIR, 'Scripts', 'python.exe') if os.name == 'nt' else os.path.join(VENV_DIR, 'bin', 'python')

# Assurez-vous que les répertoires nécessaires existent
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)

# Fonction pour activer l'environnement virtuel
def activate_venv():
    """Vérifie si l'environnement virtuel existe et l'active"""
    if not os.path.exists(VENV_DIR):
        print("L'environnement virtuel n'existe pas. Création en cours...")
        if os.name == 'nt':  # Windows
            subprocess.run([sys.executable, '-m', 'venv', VENV_DIR], check=True)
        else:  # Linux/Mac
            subprocess.run([sys.executable, '-m', 'venv', VENV_DIR], check=True)
        
        # Installer les dépendances
        print("Installation des dépendances...")
        pip_cmd = [VENV_PYTHON, '-m', 'pip', 'install', '-r', os.path.join(BASE_DIR, 'requirements.txt')]
        subprocess.run(pip_cmd, check=True)
    return VENV_PYTHON

# Fonction pour exécuter un script avec l'environnement virtuel
def run_script(script_path, args=None):
    """Exécute un script Python avec l'environnement virtuel activé"""
    python_path = activate_venv()
    cmd = [python_path, script_path]
    if args:
        cmd.extend(args)
    
    try:
        subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de l'exécution du script: {e}")
        return False

# Fonction pour ajouter ou mettre à jour un produit
def add_product():
    """Interface pour ajouter ou mettre à jour un produit à suivre"""
    # Charger les produits existants
    products = []
    if os.path.exists(PRODUCTS_JSON):
        try:
            with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
                products = json.load(f)
        except json.JSONDecodeError:
            print("Erreur lors de la lecture du fichier de produits. Création d'un nouveau fichier.")
    
    print("\n===== AJOUT D'UN PRODUIT À SUIVRE =====")
    
    # Demander les informations du produit
    product_name = input("Nom du produit: ")
    product_url = input("URL du produit: ")
    
    # Générer un ID unique pour le produit
    import hashlib
    product_id = hashlib.md5(product_url.encode()).hexdigest()[:8]
    
    # Demander le sélecteur CSS pour le prix
    print("\nSélecteur CSS pour le prix:")
    print("Par défaut: Laissez vide pour une détection automatique")
    print("Exemple: .price-box .price")
    css_selector = input("Sélecteur CSS: ")
    if not css_selector:
        css_selector = "auto"  # La détection automatique sera gérée par le scraper
    
    # Demander les paramètres de notification
    notify_on_drop = input("Notification en cas de baisse de prix? (o/n): ").lower() == 'o'
    notify_on_threshold = input("Notification si le prix descend en dessous d'un seuil? (o/n): ").lower() == 'o'
    
    threshold_price = None
    if notify_on_threshold:
        while True:
            try:
                threshold_price = float(input("Prix seuil: "))
                break
            except ValueError:
                print("Veuillez entrer un nombre valide")
    
    # Créer l'objet produit
    new_product = {
        "id": product_id,
        "name": product_name,
        "url": product_url,
        "css_selector": css_selector,
        "notify_on_drop": notify_on_drop,
        "notify_on_threshold": notify_on_threshold
    }
    
    if threshold_price is not None:
        new_product["threshold_price"] = threshold_price
    
    # Vérifier si le produit existe déjà
    product_exists = False
    for i, product in enumerate(products):
        if product["id"] == product_id or product["url"] == product_url:
            products[i] = new_product
            product_exists = True
            print(f"\nProduit '{product_name}' mis à jour avec succès!")
            break
    
    # Ajouter le produit s'il n'existe pas
    if not product_exists:
        products.append(new_product)
        print(f"\nProduit '{product_name}' ajouté avec succès!")
    
    # Enregistrer les produits
    with open(PRODUCTS_JSON, 'w', encoding='utf-8') as f:
        json.dump(products, f, indent=2, ensure_ascii=False)
    
    # Demander à l'utilisateur s'il veut vérifier le prix maintenant
    if input("\nVoulez-vous vérifier le prix maintenant? (o/n): ").lower() == 'o':
        print(f"\nVérification du prix pour '{product_name}'...")
        process_product(product_id)

# Fonction pour vérifier le prix d'un produit spécifique
def process_product(product_id=None):
    """Traite un produit spécifique ou tous les produits"""
    processor_script = os.path.join(SCRIPTS_DIR, 'processor.py')
    if product_id:
        # Implémentation spécifique pour un seul produit
        # Nous devons passer l'ID du produit au script processor.py
        # Si processor.py ne supporte pas cela directement, nous pouvons modifier le script
        # ou utiliser une solution temporaire
        
        # Charger tous les produits
        with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        # Trouver le produit spécifique
        product = next((p for p in products if p["id"] == product_id), None)
        
        if product:
            print(f"Traitement du produit: {product['name']}")
            from scripts.processor import process_product
            result = process_product(product)
            if result is not None:
                print(f"Prix actuel: {result}")
            else:
                print("Impossible de récupérer le prix. Vérifiez les logs pour plus de détails.")
        else:
            print(f"Produit avec ID {product_id} non trouvé.")
    else:
        # Traiter tous les produits
        run_script(processor_script)

# Fonction pour lancer le tableau de bord
def start_dashboard():
    """Lance le tableau de bord de suivi des prix"""
    dashboard_script = os.path.join(SCRIPTS_DIR, 'start_dashboard.py')
    print("Démarrage du tableau de bord...")
    run_script(dashboard_script)

# Fonction pour nettoyer les fichiers temporaires
def cleanup_files():
    """Nettoie les fichiers temporaires et inutiles"""
    # Vérifier si nous avons le script de nettoyage spécifique
    cleanup_script = os.path.join(SCRIPTS_DIR, 'cleanup.py')
    if os.path.exists(cleanup_script):
        print("\n===== NETTOYAGE DES FICHIERS TEMPORAIRES =====")
        print("Utilisation du script de nettoyage spécialisé...")
        run_script(cleanup_script)
        return
        
    # Sinon, utiliser la méthode par défaut
    print("Nettoyage des fichiers temporaires...")
    
    # Supprimer les dossiers __pycache__
    for root, dirs, files in os.walk(BASE_DIR):
        if '__pycache__' in dirs:
            pycache_dir = os.path.join(root, '__pycache__')
            print(f"Suppression de {pycache_dir}")
            shutil.rmtree(pycache_dir)
    
    # Supprimer les fichiers .pyc
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.pyc'):
                pyc_file = os.path.join(root, file)
                print(f"Suppression de {pyc_file}")
                os.remove(pyc_file)
    
    print("Nettoyage terminé!")

# Fonction pour nettoyer les fichiers inutilisés
def cleanup_unused_files():
    """Nettoie les fichiers inutilisés et obsolètes du projet"""
    # Options disponibles
    print("\n===== NETTOYAGE DES FICHIERS INUTILISÉS =====")
    print("1. Nettoyage standard (fichiers obsolètes et redondants)")
    print("2. Nettoyage complet (y compris tests et fichiers inutilisables)")
    print("3. Nettoyage rapide (sans confirmation)")
    print("4. Retour au menu principal")
    
    choice = input("\nChoisissez une option: ")
    
    if choice == "1":
        # Nettoyage standard
        cleanup_script = os.path.join(BASE_DIR, 'nettoyer_fichiers.py')
        
        if os.path.exists(cleanup_script):
            print("\nLancement du nettoyage standard...")
            run_script(cleanup_script)
        else:
            # Utiliser le script batch si disponible
            cleanup_batch = os.path.join(BASE_DIR, 'nettoyer_fichiers.bat')
            if os.path.exists(cleanup_batch) and os.name == 'nt':
                print("\nLancement du script de nettoyage...")
                os.system(f'start "" "{cleanup_batch}"')
            else:
                print("Les scripts de nettoyage des fichiers inutilisés n'existent pas.")
    
    elif choice == "2":
        # Nettoyage complet (suppression des tests et fichiers inutilisables)
        if os.name == 'nt':
            # Utiliser le script batch pour Windows
            print("\nLancement du nettoyage complet...")
            print("ATTENTION: Tous les fichiers de test et fichiers inutilisables vont être supprimés!")
            confirm = input("Êtes-vous sûr de vouloir continuer? (OUI/non): ")
            if confirm.upper() == "OUI":
                os.system(f'start "" "{os.path.join(BASE_DIR, "nettoyer_fichiers.bat")}"')
            else:
                print("Opération annulée.")
        else:
            # Utiliser le script PowerShell pour Linux/Mac
            ps_script = os.path.join(BASE_DIR, 'nettoyer_fichiers.ps1')
            if os.path.exists(ps_script):
                print("\nLancement du nettoyage complet...")
                if sys.platform == 'darwin':  # macOS
                    os.system(f'pwsh {ps_script}')
                else:  # Linux
                    os.system(f'pwsh {ps_script}')
            else:
                print("Le script de nettoyage complet n'existe pas.")
    
    elif choice == "3":
        # Nettoyage rapide (sans confirmation)
        if os.name == 'nt':
            # Utiliser le script batch pour Windows
            rapid_script = os.path.join(BASE_DIR, 'nettoyer_rapide.bat')
            if os.path.exists(rapid_script):
                print("\nLancement du nettoyage rapide...")
                os.system(f'start "" "{rapid_script}"')
            else:
                print("Le script de nettoyage rapide n'existe pas.")
        else:
            # Utiliser une commande directe pour Linux/Mac
            print("\nLancement du nettoyage rapide...")            # Supprimer __pycache__ et .pyc
            os.system(f'find {BASE_DIR} -name "__pycache__" -type d -exec rm -rf {{}} +')
            os.system(f'find {BASE_DIR} -name "*.pyc" -type f -delete')
            # Supprimer les fichiers temporaires
            os.system(f'find {BASE_DIR} -name "*.bak" -o -name "*.tmp" -o -name "*~" -type f -delete')
            print("Nettoyage rapide terminé!")
    
    elif choice == "4":
        # Retour au menu principal
        return
    
    else:
        print("Option invalide.")
        return

# Fonction pour lancer Airflow
def start_airflow():
    """Lance Apache Airflow pour automatiser le suivi des prix"""
    print("\n===== DÉMARRAGE D'APACHE AIRFLOW =====")
    
    # Vérifier les différentes versions disponibles
    airflow_windows_bat = os.path.join(BASE_DIR, 'airflow_windows.bat')
    airflow_script_v2 = os.path.join(BASE_DIR, 'demarrer_airflow_v2.py')
    airflow_script_optimise = os.path.join(BASE_DIR, 'demarrer_airflow_optimise.bat')
    airflow_script = os.path.join(BASE_DIR, 'demarrer_airflow.py')
    airflow_windows_direct = os.path.join(BASE_DIR, 'demarrer_airflow_windows.bat')
    
    print("Plusieurs versions d'Airflow sont disponibles :")
    print("1. Version standard")
    print("2. Version optimisée (résout automatiquement les avertissements)")
    print("3. Version Windows optimisée")
    print("4. Assistant Airflow pour Windows (recommandé)")
    print("5. Démarrage direct Airflow Windows (rapide)")
    print("6. Retour au menu principal")
    
    choice = input("\nChoisissez une option: ")
    
    if choice == "1":
        if os.path.exists(airflow_script):
            print("\nDémarrage de la version standard d'Airflow...")
            print("Le serveur web sera accessible à l'adresse: http://localhost:8080")
            print("Identifiants par défaut: admin / admin")
            print("\nAppuyez sur Ctrl+C dans le terminal pour arrêter Airflow quand vous avez terminé.")
            input("\nAppuyez sur Entrée pour continuer...")
            return run_script(airflow_script)
        else:
            print("Le script de démarrage d'Airflow standard n'existe pas.")
            return False
    
    elif choice == "2":
        if os.path.exists(airflow_script_v2):
            print("\nDémarrage de la version optimisée d'Airflow...")
            print("Cette version résout automatiquement les problèmes courants comme :")
            print("- La clé de chiffrement manquante")
            print("- Les migrations de base de données")
            print("- Les dépendances manquantes")
            input("\nAppuyez sur Entrée pour continuer...")
            return run_script(airflow_script_v2)
        else:
            print("Le script de démarrage d'Airflow optimisé n'existe pas.")
            return False
    
    elif choice == "3":
        if os.path.exists(airflow_script_optimise) and os.name == 'nt':
            print("\nDémarrage de la version Windows optimisée d'Airflow...")
            print("Cette version démarre Airflow en arrière-plan dans des fenêtres séparées.")
            input("\nAppuyez sur Entrée pour continuer...")
            os.system(f'start "" "{airflow_script_optimise}"')
            return True
        else:
            print("Le script de démarrage d'Airflow pour Windows n'existe pas ou vous n'êtes pas sous Windows.")
            return False
    
    elif choice == "4":
        if os.path.exists(airflow_windows_bat) and os.name == 'nt':
            print("\nLancement de l'Assistant Airflow pour Windows...")
            print("Cet assistant vous aidera à diagnostiquer, corriger et exécuter Airflow sur Windows.")
            input("\nAppuyez sur Entrée pour continuer...")
            os.system(f'start "" "{airflow_windows_bat}"')
            return True
        else:
            print("L'Assistant Airflow pour Windows n'existe pas ou vous n'êtes pas sous Windows.")
            return False
    
    elif choice == "5":
        if os.path.exists(airflow_windows_direct) and os.name == 'nt':
            print("\nDémarrage direct d'Airflow pour Windows...")
            print("Cette version est optimisée pour éviter les erreurs 'No module named pwd' sur Windows.")
            print("Le serveur web sera accessible à l'adresse: http://localhost:8080")
            input("\nAppuyez sur Entrée pour continuer...")
            os.system(f'start "" "{airflow_windows_direct}"')
            return True
        else:
            print("Le script de démarrage direct pour Windows n'existe pas ou vous n'êtes pas sous Windows.")
            return False
    
    elif choice == "6":
        return True
    
    else:
        print("Option invalide.")
        return False

# Fonction pour exécuter des tâches Airflow
def run_airflow_tasks():
    """Interface pour exécuter des tâches Airflow manuellement"""
    airflow_tasks_script = os.path.join(BASE_DIR, 'airflow_taches.py')
    
    if not os.path.exists(airflow_tasks_script):
        print("Le script de gestion des tâches Airflow n'existe pas.")
        return False
    
    return run_script(airflow_tasks_script)

# Fonction pour lister les produits
def list_products():
    """Liste tous les produits suivis"""
    if not os.path.exists(PRODUCTS_JSON):
        print("Aucun produit n'est encore suivi.")
        return
    
    try:
        with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
            products = json.load(f)
        
        if not products:
            print("Aucun produit n'est encore suivi.")
            return
        
        print("\n===== PRODUITS SUIVIS =====")
        for i, product in enumerate(products, 1):
            threshold = product.get('threshold_price', 'Non défini')
            notify_drop = "Oui" if product.get('notify_on_drop', False) else "Non"
            notify_threshold = "Oui" if product.get('notify_on_threshold', False) else "Non"
            
            print(f"{i}. {product['name']}")
            print(f"   ID: {product['id']}")
            print(f"   URL: {product['url']}")
            print(f"   Notification baisse de prix: {notify_drop}")
            print(f"   Notification seuil de prix: {notify_threshold}")
            print(f"   Prix seuil: {threshold}")
            print()
        
    except json.JSONDecodeError:
        print("Erreur lors de la lecture du fichier de produits.")

# Menu principal
def main_menu():
    """Affiche le menu principal interactif"""
    while True:
        print("\n===== SUIVI DES PRIX E-COMMERCE =====")
        print("1. Ajouter/Modifier un produit à suivre")
        print("2. Lister les produits suivis")
        print("3. Vérifier les prix maintenant")
        print("4. Lancer le tableau de bord")
        print("5. Générer des graphiques de tendance")
        print("6. Nettoyer les fichiers temporaires")
        print("7. Nettoyer les fichiers inutilisés")
        print("8. Démarrer Apache Airflow")
        print("9. Exécuter des tâches Airflow")
        print("0. Quitter")
        
        choice = input("\nChoisissez une option: ")
        
        if choice == '1':
            add_product()
        elif choice == '2':
            list_products()
        elif choice == '3':
            process_product()
        elif choice == '4':
            start_dashboard()
        elif choice == '5':
            visualizer_script = os.path.join(SCRIPTS_DIR, 'visualizer.py')
            run_script(visualizer_script)
        elif choice == '6':
            cleanup_files()
        elif choice == '7':
            cleanup_unused_files()
        elif choice == '8':
            start_airflow()
        elif choice == '9':
            run_airflow_tasks()
        elif choice == '0':
            print("Au revoir!")
            sys.exit(0)
        else:
            print("Option invalide. Veuillez réessayer.")

if __name__ == "__main__":
    # Vérifier si c'est la première exécution
    first_run = not os.path.exists(PRODUCTS_JSON)
    
    if first_run:
        print("Bienvenue dans le système de suivi des prix e-commerce!")
        print("Configuration initiale en cours...")
        activate_venv()
        print("Configuration terminée!\n")
    
    main_menu()
