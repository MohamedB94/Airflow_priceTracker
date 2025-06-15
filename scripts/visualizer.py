import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import logging

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('price_visualizer')

# Définition des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PRICES_CSV = os.path.join(DATA_DIR, 'prices.csv')
PRODUCTS_CSV = os.path.join(DATA_DIR, 'products.csv')
CHARTS_DIR = os.path.join(DATA_DIR, 'charts')

# S'assure que le répertoire des graphiques existe
os.makedirs(CHARTS_DIR, exist_ok=True)

def load_price_data(days=30):
    """Charge les données de prix depuis le fichier CSV"""
    if not os.path.exists(PRICES_CSV):
        logger.error(f"Fichier de prix non trouvé: {PRICES_CSV}")
        return None
    
    try:
        # Charge les données de prix
        df = pd.read_csv(PRICES_CSV)
        
        # Convertit la colonne date en datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Filtre pour les N derniers jours
        if days:
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df['date'] >= cutoff_date]
        
        return df
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données de prix: {e}")
        return None

def load_product_data():
    """Charge les données des produits depuis le fichier CSV"""
    if not os.path.exists(PRODUCTS_CSV):
        logger.error(f"Fichier de produits non trouvé: {PRODUCTS_CSV}")
        return None
    
    try:
        return pd.read_csv(PRODUCTS_CSV)
    except Exception as e:
        logger.error(f"Erreur lors du chargement des données de produits: {e}")
        return None

def generate_price_chart(product_id=None, days=30, save_path=None):
    """Génère un graphique de tendance de prix pour un produit spécifique ou tous les produits"""
    # Charge les données
    prices_df = load_price_data(days)
    products_df = load_product_data()
    
    if prices_df is None or products_df is None or len(prices_df) == 0:
        logger.warning("Aucune donnée disponible pour générer des graphiques")
        return None
    
    # Filtre pour un produit spécifique si fourni
    if product_id:
        prices_df = prices_df[prices_df['product_id'] == product_id]
        if len(prices_df) == 0:
            logger.warning(f"Aucune donnée de prix trouvée pour l'ID de produit: {product_id}")
            return None
    
    # Fusionne avec les données de produit pour obtenir les noms
    df = pd.merge(
        prices_df, 
        products_df[['product_id', 'title']], 
        on='product_id', 
        how='left'
    )
      # Configure la visualisation
    sns.set_style("whitegrid")
    plt.figure(figsize=(12, 8))
    
    # Génère le graphique linéaire
    ax = sns.lineplot(
        data=df,
        x='date',
        y='price',
        hue='title',
        marker='o',
        linewidth=2.5
    )
    
    # Définit le titre et les étiquettes du graphique
    if product_id:
        product_name = df['title'].iloc[0] if len(df) > 0 else 'Produit Inconnu'
        plt.title(f'Tendance de prix pour {product_name} - {days} derniers jours', fontsize=16)
    else:
        plt.title(f'Tendances de prix pour tous les produits - {days} derniers jours', fontsize=16)
    
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Prix', fontsize=12)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Ajoute une grille
    plt.grid(True, linestyle='--', alpha=0.7)
      # Génère le nom de fichier s'il n'est pas fourni
    if not save_path:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if product_id:
            filename = f'tendance_prix_{product_id}_{timestamp}.png'
        else:
            filename = f'tendances_prix_tous_{timestamp}.png'
        save_path = os.path.join(CHARTS_DIR, filename)
    
    # Enregistre le graphique
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Graphique de prix généré et enregistré dans: {save_path}")
    return save_path

def generate_all_charts(days=30):
    """Génère des graphiques individuels pour chaque produit et un graphique combiné"""
    # Charge les données
    prices_df = load_price_data(days)
    products_df = load_product_data()
    
    if prices_df is None or products_df is None or len(prices_df) == 0:
        logger.warning("Aucune donnée disponible pour générer des graphiques")
        return []
    
    # Génère un horodatage pour les noms de fichiers
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
      # Génère des graphiques individuels pour chaque produit
    chart_paths = []
    for product_id in prices_df['product_id'].unique():
        # Obtient les informations du produit
        product_info = products_df[products_df['product_id'] == product_id]
        if len(product_info) == 0:
            continue
            
        product_name = product_info['title'].iloc[0]
        filename = f'tendance_prix_{product_id}_{timestamp}.png'
        save_path = os.path.join(CHARTS_DIR, filename)
        
        # Génère et enregistre le graphique
        generated_path = generate_price_chart(product_id, days, save_path)
        if generated_path:
            chart_paths.append(generated_path)
    
    # Génère un graphique combiné pour tous les produits
    combined_path = os.path.join(CHARTS_DIR, f'tendances_prix_tous_{timestamp}.png')
    generated_path = generate_price_chart(None, days, combined_path)
    if generated_path:
        chart_paths.append(generated_path)
    
    return chart_paths

if __name__ == "__main__":
    # Teste le module de visualisation
    chart_paths = generate_all_charts(30)
    print(f"Généré {len(chart_paths)} graphiques")
