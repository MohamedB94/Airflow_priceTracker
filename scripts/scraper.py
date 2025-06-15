import requests
from bs4 import BeautifulSoup
import sys
import json
import logging
import time
import random
import os
from urllib.parse import urlparse
from scripts.user_agents import get_random_user_agent
from scripts.ecommerce_parser import EcommerceParser

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('price_scraper')

# Create a cache directory if it doesn't exist
CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'cache')
os.makedirs(CACHE_DIR, exist_ok=True)

def get_price(url, css_selector, retries=3, delay=2, use_cache=True, cache_duration=3600):
    """
    Récupère le prix depuis un site web en utilisant le sélecteur CSS fourni.
    Inclut la logique de réessai, des délais aléatoires et la mise en cache pour éviter d'être bloqué.
    
    Args:
        url (str): L'URL de la page du produit
        css_selector (str): Sélecteur CSS pour l'élément de prix
        retries (int): Nombre de tentatives de réessai
        delay (int): Délai de base entre les réessais en secondes
        use_cache (bool): Utiliser ou non les réponses mises en cache
        cache_duration (int): Durée de validité du cache en secondes
    
    Returns:
        dict: Informations sur le produit incluant le prix, le titre, etc.
    """
    # Générer un nom de fichier de cache basé sur l'URL
    cache_file = None
    if use_cache:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        path_hash = hash(parsed_url.path)
        cache_file = os.path.join(CACHE_DIR, f"{domain}_{path_hash}.html")
        
        # Vérifier si nous avons une réponse en cache valide
        if os.path.exists(cache_file):
            file_age = time.time() - os.path.getmtime(cache_file)
            if file_age < cache_duration:
                logger.info(f"Utilisation de la réponse en cache pour {url}")
                try:
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    # Analyser le HTML en cache
                    result = EcommerceParser.parse_page(html_content, url, css_selector)
                    
                    # S'assurer d'avoir tous les champs attendus par le reste de l'application
                    return {
                        "price": result["price_text"],
                        "title": result["title"],
                        "currency": result["currency"],
                        "status": "success" if result["price_text"] else "error",
                        "numeric_price": result["numeric_price"],
                        "availability": result["availability"],
                        "image_url": result["image_url"],
                        "url": url,
                        "source": "cache"
                    }
                except Exception as e:
                    logger.warning(f"Erreur lors de l'utilisation de la réponse en cache: {e}")
                    # Continuer avec une nouvelle requête si le cache échoue
    
    # Configuration des en-têtes avec un user agent aléatoire
    headers = {
        "User-Agent": get_random_user_agent(),
        "Accept-Language": "fr-FR,fr;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache",
    }
    
    for attempt in range(retries):
        try:
            # Ajouter un délai aléatoire pour imiter un comportement humain
            if attempt > 0:
                sleep_time = delay + random.uniform(1, 3)
                logger.info(f"Tentative {attempt+1}/{retries} - Attente de {sleep_time:.2f} secondes")
                time.sleep(sleep_time)
            
            logger.info(f"Récupération du prix depuis: {url}")
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Sauvegarder la réponse dans le cache si activé
            if use_cache and cache_file:
                try:
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        f.write(response.text)
                    logger.debug(f"Réponse sauvegardée dans le cache: {cache_file}")
                except Exception as e:
                    logger.warning(f"Échec de sauvegarde dans le cache: {e}")
            
            # Utiliser le parser e-commerce pour extraire les données
            result = EcommerceParser.parse_page(response.text, url, css_selector)
            
            if result["price_text"]:
                logger.info(f"Prix trouvé: {result['price_text']}")
                
                return {
                    "price": result["price_text"],
                    "title": result["title"],
                    "currency": result["currency"],
                    "status": "success",
                    "numeric_price": result["numeric_price"],
                    "availability": result["availability"],
                    "image_url": result["image_url"],
                    "url": url,
                    "source": "live"
                }
            else:
                logger.warning(f"Élément de prix non trouvé avec le sélecteur: {css_selector}")
                # Essayer des sélecteurs spécifiques au site comme solution de repli
                if result["title"] != "Produit Inconnu":
                    logger.info(f"Titre du produit trouvé: {result['title']}, mais pas de prix avec le sélecteur fourni.")
        except requests.exceptions.HTTPError as e:
            logger.error(f"Erreur HTTP: {e}")
            if e.response.status_code == 403:
                logger.warning("Blocage possible détecté. Envisagez d'utiliser un proxy pour ce site.")
        except requests.exceptions.ConnectionError:
            logger.error(f"Erreur de connexion - tentative {attempt+1}/{retries}")
        except requests.exceptions.Timeout:
            logger.error(f"Erreur de délai d'attente - tentative {attempt+1}/{retries}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Exception de requête: {e}")
        except Exception as e:
            logger.error(f"Erreur inattendue: {e}")
    
    return {
        "price": None,
        "title": "Produit Inconnu",
        "currency": "Inconnu",
        "status": "error",
        "message": "Échec de récupération du prix après plusieurs tentatives",
        "url": url,
        "source": "error"
    }

if __name__ == "__main__":
    import argparse
    
    # Create command line argument parser
    parser = argparse.ArgumentParser(description='Scrape product prices from e-commerce websites')
    parser.add_argument('url', help='URL of the product page')
    parser.add_argument('--selector', '-s', help='CSS selector for the price element')
    parser.add_argument('--no-cache', action='store_true', help='Disable response caching')
    parser.add_argument('--retries', '-r', type=int, default=3, help='Number of retry attempts')
    parser.add_argument('--detect', '-d', action='store_true', help='Detect site and suggest selectors')
    
    args = parser.parse_args()
    
    if args.detect:
        # Just detect the site and suggest selectors
        site = EcommerceParser.detect_site(args.url)
        selectors = EcommerceParser.get_selectors(site)
        print(f"Detected site: {site}")
        print("Recommended selectors:")
        for element_type, selector_list in selectors.items():
            print(f"  {element_type}: {selector_list[0]}")
        sys.exit(0)
    
    # Run the scraper
    result = get_price(
        args.url, 
        args.selector, 
        retries=args.retries, 
        use_cache=not args.no_cache
    )
    
    # Print nicely formatted result
    if result["status"] == "success":
        print(f"\n{'='*50}")
        print(f"Product: {result['title']}")
        print(f"Price: {result['price']}")
        if result.get('numeric_price'):
            print(f"Numeric Price: {result['numeric_price']}")
        print(f"Currency: {result['currency']}")
        if result.get('availability'):
            print(f"Availability: {result['availability']}")
        print(f"Source: {result.get('source', 'Unknown')}")
        print(f"{'='*50}\n")
    else:
        print(f"\nError: {result.get('message', 'Unknown error')}")
    
    # Also output as JSON for programmatic use
    print(json.dumps(result, indent=2))
