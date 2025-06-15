import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('price_notifier')

# Email configuration (update with your SMTP details)
SMTP_SERVER = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USERNAME = os.environ.get('SMTP_USERNAME', '')
SMTP_PASSWORD = os.environ.get('SMTP_PASSWORD', '')
EMAIL_FROM = os.environ.get('EMAIL_FROM', '')
EMAIL_TO = os.environ.get('EMAIL_TO', '')

def send_email_notification(subject, message, to_email=None):
    """Envoyer une notification par email"""
    if not all([SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD, EMAIL_FROM]):
        logger.warning("Configuration email incomplète. Notification ignorée.")
        return False
    
    to_email = to_email or EMAIL_TO
    if not to_email:
        logger.warning("Aucun destinataire spécifié. Notification ignorée.")
        return False
    
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = EMAIL_FROM
        msg['To'] = to_email
        
        # Add timestamp to message
        full_message = f"{message}\n\nEnvoyé le: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
          # Create HTML version of message
        html_message = f"""
        <html>
          <head></head>
          <body>
            <p>{full_message.replace(chr(10), '<br>')}</p>
          </body>
        </html>
        """
          # Attach both plain text and HTML versions
        msg.attach(MIMEText(full_message, 'plain'))
        msg.attach(MIMEText(html_message, 'html'))
        
        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.send_message(msg)
        
        logger.info(f"Email de notification envoyé à {to_email}")
        return True
    
    except Exception as e:
        logger.error(f"Échec de l'envoi de l'email de notification: {e}")
        return False

def notify_price_drop(product_name, old_price, new_price, product_url, currency='€'):
    """Envoyer une notification quand le prix d'un produit baisse"""
    subject = f"Alerte Baisse de Prix: {product_name}"
    
    message = f"""
Alerte Baisse de Prix !

Produit: {product_name}
Ancien Prix: {currency}{old_price}
Nouveau Prix: {currency}{new_price}
Vous Économisez: {currency}{old_price - new_price} ({round((old_price - new_price) / old_price * 100, 2)}%)

Voir le produit: {product_url}
    """
    
    return send_email_notification(subject, message)

def notify_threshold_reached(product_name, price, threshold, product_url, currency='€'):
    """Envoyer une notification quand le prix d'un produit passe sous le seuil défini"""
    subject = f"Alerte Seuil de Prix: {product_name}"
    
    message = f"""
Alerte Seuil de Prix !

Produit: {product_name}
Prix Actuel: {currency}{price}
Seuil: {currency}{threshold}

Le prix est maintenant en dessous de votre seuil défini !

Voir le produit: {product_url}
    """
    
    return send_email_notification(subject, message)

if __name__ == "__main__":
    # Test the notification module
    notify_price_drop(
        "Produit Test", 
        100.00, 
        85.00, 
        "https://example.com/product",
        "€"
    )
