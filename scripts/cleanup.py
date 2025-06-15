#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import sys
from datetime import datetime

def clean_files():
    """Nettoie les fichiers temporaires et les caches"""
    print("Nettoyage des fichiers temporaires...")
    
    # Définition des chemins
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Compteurs pour les statistiques
    pycache_count = 0
    pyc_count = 0
    
    # Supprimer les dossiers __pycache__
    for root, dirs, files in os.walk(base_dir):
        if '__pycache__' in dirs:
            pycache_dir = os.path.join(root, '__pycache__')
            print(f"Suppression de {pycache_dir}")
            try:
                shutil.rmtree(pycache_dir)
                pycache_count += 1
            except Exception as e:
                print(f"Erreur lors de la suppression de {pycache_dir}: {e}")
    
    # Supprimer les fichiers .pyc
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file.endswith('.pyc'):
                pyc_file = os.path.join(root, file)
                print(f"Suppression de {pyc_file}")
                try:
                    os.remove(pyc_file)
                    pyc_count += 1
                except Exception as e:
                    print(f"Erreur lors de la suppression de {pyc_file}: {e}")
    
    # Supprimer le dossier cache s'il existe
    cache_dir = os.path.join(base_dir, 'cache')
    if os.path.exists(cache_dir):
        print(f"Suppression du dossier cache: {cache_dir}")
        try:
            shutil.rmtree(cache_dir)
        except Exception as e:
            print(f"Erreur lors de la suppression du dossier cache: {e}")
    
    # Nettoyer les logs anciens
    logs_dir = os.path.join(base_dir, 'logs')
    log_files_cleaned = 0
    
    if os.path.exists(logs_dir):
        for root, dirs, files in os.walk(logs_dir):
            for file in files:
                # Nettoie les logs de plus de 30 jours ou les logs de backup
                if file.endswith('.log.1') or file.endswith('.log.2'):
                    log_file = os.path.join(root, file)
                    print(f"Suppression du log: {log_file}")
                    try:
                        os.remove(log_file)
                        log_files_cleaned += 1
                    except Exception as e:
                        print(f"Erreur lors de la suppression de {log_file}: {e}")
    
    # Afficher un résumé
    print("\nNettoyage terminé!")
    print(f"- {pycache_count} dossiers __pycache__ supprimés")
    print(f"- {pyc_count} fichiers .pyc supprimés")
    print(f"- {log_files_cleaned} fichiers de log nettoyés")
    
    if os.path.exists(cache_dir):
        print("⚠️ Attention: Le dossier cache n'a pas pu être supprimé entièrement")
    else:
        print("- Dossier cache supprimé avec succès")

if __name__ == "__main__":
    clean_files()
    
    # Si on est sur Windows et que le script est lancé directement (pas importé)
    if os.name == 'nt' and not hasattr(sys, 'ps1'):
        input("\nAppuyez sur Entrée pour quitter...")
