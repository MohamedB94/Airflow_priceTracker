"""
Sélecteurs spécifiques aux sites e-commerce et logique d'analyse.
Ce module fournit une gestion spécialisée pour différentes plateformes e-commerce.
"""
import logging
import re
from bs4 import BeautifulSoup

logger = logging.getLogger('ecommerce_parser')

class EcommerceParser:
    """Classe d'analyse pour les sites web e-commerce avec une logique spécifique au site."""
    
    @staticmethod
    def detect_site(url):
        """Détecter à quel site e-commerce appartient l'URL."""
        if "amazon" in url:
            return "amazon"
        elif "cdiscount" in url:
            return "cdiscount"
        elif "fnac" in url:
            return "fnac"
        elif "darty" in url:
            return "darty"
        elif "boulanger" in url:
            return "boulanger"
        elif "leclerc" in url:
            return "leclerc"
        else:
            return "generic"
    
    @staticmethod
    def get_selectors(site):
        """Obtenir les sélecteurs CSS appropriés pour un site donné."""
        selectors = {
            "amazon": {
                "price": [".a-price .a-offscreen", ".a-price-whole", "#priceblock_ourprice", "#priceblock_dealprice", ".a-section .a-color-price"],
                "title": ["#productTitle", "#title", ".product-title-word-break"],
                "availability": ["#availability", "#deliveryMessageMirId", ".a-section.a-spacing-base"],
                "image": ["#landingImage", "#imgBlkFront", "#main-image"]
            },
            "cdiscount": {
                "price": [".fpPrice", ".price", ".jsMainPrice"],
                "title": ["h1", ".fpDesColumn h1", ".prdtBILTit"],
                "availability": [".fpStockLevel", ".stockLevel", ".fpStockLevelBar"],
                "image": [".prdtVisual img", ".jsPrdtBlocImg img"]
            },
            "fnac": {
                "price": [".userPrice", ".f-priceBox__price", ".Article-price"],
                "title": [".f-productHeader-Title", ".Article-infoContent h1"],
                "availability": [".f-buyBox-availabilityStatus", ".Article-availability"],
                "image": [".f-productVisuals-mainVisual img", ".Article-imageContainer img"]
            },
            "darty": {
                "price": [".product_price", ".price", ".darty_prix_produit"],
                "title": [".product_name", "h1.product_title"],
                "availability": [".availability-msg", ".product_stock"],
                "image": [".product_image img", ".product_img img"]
            },
            "boulanger": {
                "price": [".price__amount", ".main-price", ".price"],
                "title": [".product-title", "h1.title"],
                "availability": [".product-availability", ".stock-notification"],
                "image": [".product-gallery img", ".carousel-item img"]
            },
            "leclerc": {
                "price": [".product-price", ".price", ".current-price"],
                "title": [".product-title", ".product-name", "h1"],
                "availability": [".availability", ".stock-status"],
                "image": [".product-image img", ".main-image img"]
            },
            "generic": {
                "price": [".price", ".product-price", "[itemprop='price']", ".current-price", ".sales-price"],
                "title": ["h1", ".product-title", "[itemprop='name']", ".product-name"],
                "availability": [".availability", ".stock-status", "[itemprop='availability']"],
                "image": [".product-image img", "[itemprop='image']", ".main-image img"]
            }
        }
        return selectors.get(site, selectors["generic"])
    
    @staticmethod
    def clean_price(price_text, currency_symbols=('€', '$', '£', '¥')):
        """
        Extract numeric price from text, handling various formats and currencies.
        """
        if not price_text or price_text.lower() == 'none':
            return None
        
        # Remove currency symbols and spaces
        for symbol in currency_symbols:
            price_text = price_text.replace(symbol, '')
        
        # Remove non-breaking spaces and other whitespace
        price_text = price_text.replace('\xa0', ' ').strip()
        
        # Try to extract a numeric value using regex
        price_match = re.search(r'(\d+[.,]?\d*)', price_text)
        if price_match:
            price_str = price_match.group(1)
            # Handle different decimal separators
            price_str = price_str.replace(',', '.')
            try:
                return float(price_str)
            except ValueError:
                logger.warning(f"Could not convert price string to float: {price_str}")
                return None
        else:
            logger.warning(f"No numeric price found in text: {price_text}")
            return None
    
    @staticmethod
    def extract_currency(price_text):
        """Extract currency symbol from price text."""
        for symbol in ('€', '$', '£', '¥'):
            if symbol in price_text:
                return symbol
        return "Unknown"
    
    @staticmethod
    def extract_data(soup, selectors, element_type):
        """Try multiple selectors to extract data from the page."""
        for selector in selectors.get(element_type, []):
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return None
    
    @staticmethod
    def parse_page(html_content, url, css_selector=None):
        """
        Parse e-commerce page and extract product data.
        If a specific CSS selector is provided, it will be used for the price.
        Otherwise, site-specific selectors will be tried.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        site = EcommerceParser.detect_site(url)
        selectors = EcommerceParser.get_selectors(site)
        
        # Extract price
        price_text = None
        if css_selector:
            # Use provided selector if available
            element = soup.select_one(css_selector)
            if element:
                price_text = element.get_text(strip=True)
        
        # If no price found with provided selector, try site-specific selectors
        if not price_text:
            price_text = EcommerceParser.extract_data(soup, selectors, "price")
        
        # Extract other product data
        title = EcommerceParser.extract_data(soup, selectors, "title")
        availability = EcommerceParser.extract_data(soup, selectors, "availability")
        
        # Get image URL
        image_url = None
        for selector in selectors.get("image", []):
            img_element = soup.select_one(selector)
            if img_element and img_element.has_attr('src'):
                image_url = img_element['src']
                # Handle relative URLs
                if image_url and image_url.startswith('/'):
                    from urllib.parse import urlparse
                    parsed_url = urlparse(url)
                    image_url = f"{parsed_url.scheme}://{parsed_url.netloc}{image_url}"
                break
        
        # Clean and extract numeric price
        numeric_price = EcommerceParser.clean_price(price_text) if price_text else None
        currency = EcommerceParser.extract_currency(price_text) if price_text else "Unknown"
        
        return {
            "price_text": price_text,
            "numeric_price": numeric_price,
            "currency": currency,
            "title": title or "Unknown Product",
            "availability": availability,
            "image_url": image_url,
            "site": site
        }
