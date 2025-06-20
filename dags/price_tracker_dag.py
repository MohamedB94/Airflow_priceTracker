from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
import os
import sys
import json
import logging

# Add scripts directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

# Import our modules
from scripts.processor import process_all_products
from scripts.visualizer import generate_all_charts

# Define base directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCRIPTS_DIR = os.path.join(BASE_DIR, 'scripts')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('price_tracker_dag')

# Configuration du DAG
default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2025, 6, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

# Création du DAG
dag = DAG(
    'price_tracker',
    default_args=default_args,
    description='Suivi des prix des produits e-commerce',
    schedule_interval='0 */6 * * *',  # Exécution toutes les 6 heures
    catchup=False,
    tags=['e-commerce', 'suivi-prix'],
)

# Définit les fonctions à appeler par les opérateurs
def track_prices(**kwargs):
    """Suivi des prix pour tous les produits"""
    logger.info("Démarrage du processus de suivi des prix")
    results = process_all_products()
    if results:
        success_count = sum(1 for r in results if r['price'] is not None)
        logger.info(f"Suivi des prix réussi pour {success_count}/{len(results)} produits")
        # Pousse les résultats vers XCom pour les tâches en aval
        kwargs['ti'].xcom_push(key='price_tracking_results', value=results)
    return results

def generate_visualizations(**kwargs):
    """Génère des visualisations de tendance de prix"""
    logger.info("Génération des visualisations de tendance de prix")
    chart_paths = generate_all_charts(days=30)
    logger.info(f"Générés {len(chart_paths)} graphiques")
    # Pousse les chemins des graphiques vers XCom pour les tâches en aval
    kwargs['ti'].xcom_push(key='chart_paths', value=chart_paths)
    return chart_paths

# Définit les tâches
start = EmptyOperator(
    task_id='start',
    dag=dag,
)

track_prices_task = PythonOperator(
    task_id='track_prices',
    python_callable=track_prices,
    dag=dag,
)

generate_visualizations_task = PythonOperator(    task_id='generate_visualizations',
    python_callable=generate_visualizations,
    dag=dag,
)

backup_data_task = BashOperator(
    task_id='backup_data',
    bash_command=f'cp {os.path.join(BASE_DIR, "data", "prices.csv")} {os.path.join(BASE_DIR, "data", "prices_backup_$(date +%Y%m%d).csv")}',
    dag=dag,
)

end = EmptyOperator(
    task_id='end',
    dag=dag,
)

# Définition du flux de tâches
start >> track_prices_task >> backup_data_task >> generate_visualizations_task  >> end