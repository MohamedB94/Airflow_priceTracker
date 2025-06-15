FROM apache/airflow:2.7.1

# Installation des dépendances nécessaires
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt

# Génération d'une clé Fernet pour l'environnement
RUN pip install cryptography && \
    python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())" > /opt/airflow/fernet_key.txt
