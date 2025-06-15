import os
import csv
import pandas as pd
from datetime import datetime

# Chemin du fichier
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
PRICES_CSV = os.path.join(DATA_DIR, 'prices.csv')
BACKUP_CSV = os.path.join(DATA_DIR, f'prices_backup_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')

# Faire une sauvegarde du fichier original
try:
    if os.path.exists(PRICES_CSV):
        with open(PRICES_CSV, 'r') as src, open(BACKUP_CSV, 'w') as dst:
            dst.write(src.read())
        print(f"Sauvegarde créée: {BACKUP_CSV}")
except Exception as e:
    print(f"Erreur lors de la création de la sauvegarde: {str(e)}")
    exit(1)

# Structure attendue: product_id,product_name,price,currency,date
try:
    # Lire les données existantes
    data = []
    headers = ["product_id", "product_name", "price", "currency", "date"]
    
    with open(PRICES_CSV, 'r') as file:
        reader = csv.reader(file)
        for i, row in enumerate(reader):
            if i == 0:  # Ignorer l'en-tête actuel
                continue
            
            if len(row) == 2:  # Format ancien: date,prix
                date_str, price_str = row
                try:
                    price = float(price_str.replace(',', '.'))
                    data.append({
                        "product_id": "product1",
                        "product_name": "iPhone 13",
                        "price": price,
                        "currency": "€",
                        "date": date_str
                    })
                except ValueError:
                    print(f"Ignoré ligne {i+1}: {row} - Impossible de convertir le prix")
            
            elif len(row) >= 4:  # Format avec au moins 4 colonnes
                try:
                    if len(row) == 4:  # Format: date,product_id,price,currency
                        date_str, product_id, price_str, currency = row
                        product_name = "Produit inconnu"
                    elif len(row) == 5:  # Format complet: date,product_id,price,currency,availability ou product_id,product_name,price,currency,date
                        if row[0].startswith('202'):  # Si la première colonne ressemble à une date
                            date_str, product_id, price_str, currency, _ = row
                            product_name = "Produit inconnu"
                        else:
                            product_id, product_name, price_str, currency, date_str = row
                    
                    price = float(price_str.replace(',', '.'))
                    data.append({
                        "product_id": product_id,
                        "product_name": product_name,
                        "price": price,
                        "currency": currency,
                        "date": date_str
                    })
                except (ValueError, IndexError) as e:
                    print(f"Ignoré ligne {i+1}: {row} - Erreur: {str(e)}")
    
    # Écrire les données nettoyées dans un nouveau fichier CSV
    with open(PRICES_CSV, 'w', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=headers)
        writer.writeheader()
        writer.writerows(data)
    
    print(f"Fichier {PRICES_CSV} nettoyé avec succès.")
    print(f"Nombre d'entrées: {len(data)}")
    
except Exception as e:
    print(f"Erreur lors du nettoyage du fichier: {str(e)}")
    print("La sauvegarde est disponible dans: " + BACKUP_CSV)
