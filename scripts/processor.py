import os
import json
import logging
import pandas as pd
from datetime import datetime
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import other modules
from scripts.notifier import notify_price_drop, notify_threshold_reached
from scripts.scraper import get_price
from scripts.save_price import save_product_price

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs', 'price_tracker.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('price_processor')

# Définition des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PRODUCTS_JSON = os.path.join(DATA_DIR, 'products.json')
PRICES_CSV = os.path.join(DATA_DIR, 'prices.csv')
PRODUCTS_CSV = os.path.join(DATA_DIR, 'products.csv')

def load_products():
    """Charge la configuration des produits depuis le fichier JSON"""
    try:
        with open(PRODUCTS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Erreur lors du chargement de la configuration des produits: {e}")
        return []

def get_previous_price(product_id):
    """Récupère le prix précédent d'un produit depuis le fichier CSV"""
    try:
        if not os.path.exists(PRICES_CSV):
            return None
            
        df = pd.read_csv(PRICES_CSV)
        if 'product_id' not in df.columns or len(df) == 0:
            return None
            
        # Filtre par product_id et récupère le prix le plus récent
        product_prices = df[df['product_id'] == product_id]
        if len(product_prices) == 0:
            return None
            
        # Trie par date (plus récent en premier) et récupère la première ligne
        product_prices['date'] = pd.to_datetime(product_prices['date'])
        product_prices = product_prices.sort_values('date', ascending=False)
        
        return product_prices.iloc[0]['price']
    except Exception as e:
        logger.error(f"Erreur lors de la récupération du prix précédent pour le produit {product_id}: {e}")
        return None

def check_price_changes(product_data, current_price):
    """Vérifie si le prix a changé et s'il est inférieur au seuil"""
    product_id = product_data['id']
    previous_price = get_previous_price(product_id)
    
    # Ignore s'il n'y a pas de prix précédent ou si l'analyse du prix actuel a échoué
    if previous_price is None or current_price is None:
        return
    
    # Vérifie s'il y a une baisse de prix
    if current_price < previous_price and product_data.get('notify_on_drop', False):
        logger.info(f"Baisse de prix détectée pour {product_data['name']}: {previous_price} -> {current_price}")
        notify_price_drop(
            product_data['name'],
            previous_price,
            current_price,
            product_data['url'],
            product_data.get('currency', '€')
        )
    
    # Vérifie si le prix est inférieur au seuil
    threshold = product_data.get('threshold_price')
    if threshold and current_price <= threshold and product_data.get('notify_on_threshold', False):
        logger.info(f"Seuil de prix atteint pour {product_data['name']}: {current_price} <= {threshold}")
        notify_threshold_reached(
            product_data['name'],
            current_price,
            threshold,
            product_data['url'],
            product_data.get('currency', '€')
        )

def process_product(product_data):
    """Traite un seul produit: scrape le prix, l'enregistre et vérifie les changements"""
    try:
        product_id = product_data['id']
        product_name = product_data['name']
        url = product_data['url']
        css_selector = product_data['css_selector']
        
        logger.info(f"Traitement du produit: {product_name} (ID: {product_id})")
        
        # Scrape le prix
        result = get_price(url, css_selector)
        
        # Ajoute l'URL au résultat
        result['url'] = url
        
        # Enregistre le prix
        price_value = save_product_price(result, product_id)
        
        # Vérifie les changements de prix et les notifications
        if price_value is not None:
            check_price_changes(product_data, price_value)
            
        return price_value
    except Exception as e:
        logger.error(f"Erreur lors du traitement du produit {product_data.get('name', 'Inconnu')}: {e}")
        return None

def process_all_products():
    """Traite tous les produits depuis le fichier de configuration"""
    products = load_products()
    
    if not products:
        logger.warning("Aucun produit trouvé dans le fichier de configuration")
        return
    
    logger.info(f"Démarrage du suivi des prix pour {len(products)} produits")
    
    results = []
    for product in products:
        price = process_product(product)
        results.append({
            'id': product['id'],
            'name': product['name'],
            'price': price,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
    
    logger.info(f"Suivi des prix terminé pour {len(products)} produits")
    return results

if __name__ == "__main__":
    # Crée les répertoires requis
    os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    
    # Traite tous les produits
    results = process_all_products()
    
    # Affiche les résultats
    if results:
        for result in results:
            if result['price'] is not None:
                print(f"{result['name']}: {result['price']}")
            else:
                print(f"{result['name']}: Prix non disponible")
