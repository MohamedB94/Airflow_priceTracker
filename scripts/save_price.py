import sys
import csv
import os
import json
from datetime import datetime
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('price_saver')

# Définition des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PRICES_CSV = os.path.join(DATA_DIR, 'prices.csv')
PRODUCTS_CSV = os.path.join(DATA_DIR, 'products.csv')

def clean_price(price_text):
    """Nettoie la chaîne de prix pour extraire la valeur numérique"""
    import re
    if not price_text or price_text == "None":
        return None
    # Supprime les symboles de devise, espaces, etc. et ne garde que les chiffres, point et virgule
    clean = re.sub(r'[^\d.,]', '', price_text)
    # Remplace la virgule par un point pour la cohérence
    clean = clean.replace(',', '.')
    try:
        return float(clean)
    except ValueError:
        logger.error(f"Impossible de convertir le prix '{price_text}' en nombre")
        return None

def save_product_price(data, product_id=None):
    """Enregistre le prix du produit dans un fichier CSV avec les informations du produit"""
    # S'assure que le répertoire de données existe
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Analyse les données d'entrée
    if isinstance(data, str):
        try:
            data = json.loads(data)
        except json.JSONDecodeError:
            # Si ce n'est pas du JSON, suppose que c'est juste une valeur de prix
            data = {"price": data, "title": "Produit Inconnu", "status": "success"}
    
    # Extrait le prix - utilise numeric_price de notre scraper amélioré ou nettoie le prix textuel
    price_value = data.get('numeric_price')
    if price_value is None:
        price_text = data.get('price')
        price_value = clean_price(price_text)
    
    product_title = data.get('title', 'Produit Inconnu')
    status = data.get('status', 'success')
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
      # Ignore si le prix n'a pas pu être analysé ou si le statut est une erreur
    if price_value is None or status == 'error':
        logger.warning(f"Enregistrement ignoré en raison d'un prix invalide ou d'un statut d'erreur: {data}")
        return None
    
    # Si product_id n'est pas fourni, en génère un à partir du titre
    if product_id is None:
        import hashlib
        product_id = hashlib.md5(product_title.encode()).hexdigest()[:8]
    
    # Enregistre dans prices.csv
    prices_file_exists = os.path.isfile(PRICES_CSV)
    with open(PRICES_CSV, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not prices_file_exists:
            writer.writerow(['date', 'product_id', 'price', 'currency', 'availability'])
        writer.writerow([
            timestamp, 
            product_id, 
            price_value, 
            data.get('currency', 'Inconnu'),
            data.get('availability', '')
        ])
      # Met à jour ou crée un produit dans products.csv
    products_file_exists = os.path.isfile(PRODUCTS_CSV)
    products = {}
    
    # Lit les produits existants si le fichier existe
    if products_file_exists:
        with open(PRODUCTS_CSV, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                products[row['product_id']] = row
    
    # Met à jour les informations du produit
    products[product_id] = {
        'product_id': product_id,
        'title': product_title,
        'url': data.get('url', ''),
        'last_checked': timestamp,
        'last_price': price_value,
        'currency': data.get('currency', 'Inconnu'),
        'availability': data.get('availability', ''),
        'image_url': data.get('image_url', '')
    }
      # Écrit tous les produits
    with open(PRODUCTS_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['product_id', 'title', 'url', 'last_checked', 'last_price', 'currency', 'availability', 'image_url']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for product in products.values():
            writer.writerow(product)
    
    logger.info(f"Prix {price_value} enregistré pour le produit {product_title} (ID: {product_id})")
    return price_value

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Utilisation: python save_price.py <données_prix_json> [product_id]")
        sys.exit(1)
    
    price_data = sys.argv[1]
    product_id = sys.argv[2] if len(sys.argv) > 2 else None
    
    saved_price = save_product_price(price_data, product_id)
    if saved_price:
        print(f"Prix {saved_price} enregistré avec succès.")
    else:
        print("Échec de l'enregistrement du prix. Consultez les logs pour plus de détails.")
        sys.exit(1)