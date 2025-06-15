# Système de Suivi des Prix E-commerce avec Airflow

Ce projet est un système complet de suivi des prix de produits e-commerce utilisant Apache Airflow avec Docker pour l'automatisation des tâches.

## 🚀 Fonctionnalités

- **Suivi automatique des prix** : Surveillance régulière des prix de multiples produits en ligne
- **Alertes de prix** : Notifications lorsque les prix baissent ou atteignent un seuil spécifié
- **Visualisation des tendances** : Graphiques et tableaux de bord pour analyser l'évolution des prix
- **Automatisation avec Airflow** : Planification et gestion des tâches via une interface web intuitive
- **Déploiement Docker** : Environnement isolé et cohérent pour éviter les problèmes de compatibilité
- **Scraping intelligent** : Détection automatique des sélecteurs pour différents sites e-commerce
- **Interface utilisateur intuitive** : Menus interactifs pour gérer les fonctionnalités
- **Historique complet** : Données de prix stockées en CSV pour analyse à long terme
- **Dashboard interactif** : Visualisation en temps réel des tendances de prix

## 📋 Table des matières

1. [Prérequis](#prérequis)
2. [Installation](#installation)
3. [Démarrage rapide](#démarrage-rapide)
4. [Utilisation d'Airflow avec Docker](#utilisation-dairflow-avec-docker)
5. [Tableau de bord](#tableau-de-bord)
6. [Structure du projet](#structure-du-projet)
7. [DAGs et scripts](#dags-et-scripts)
8. [Dépannage](#dépannage)
9. [Solutions cloud](#solutions-cloud)

## 🔧 Prérequis

- **Docker Desktop** pour Windows (dernière version)
- **Python 3.8+** pour l'interface utilisateur locale et le tableau de bord
- **Navigateur web moderne** pour accéder aux interfaces Airflow et au tableau de bord

## 💻 Installation

### Option 1: Installation avec Docker (recommandée)

1. Assurez-vous que Docker Desktop est installé et en cours d'exécution
2. Clonez ou téléchargez ce dépôt dans `c:\xampp\htdocs\Airflow` ou tout autre emplacement de votre choix
3. Ouvrez une invite de commande ou PowerShell dans ce dossier

### Option 2: Installation Python locale (pour développement uniquement)

1. Clonez ce dépôt
2. Créez un environnement virtuel:
   ```
   python -m venv airflow_env
   ```
3. Activez l'environnement:
   ```
   airflow_env\Scripts\activate
   ```
4. Installez les dépendances:
   ```
   pip install -r requirements.txt
   ```

## 🚀 Démarrage rapide

### Interface utilisateur du suivi de prix

Pour lancer l'interface utilisateur de suivi de prix:

```
python price_tracking.py
```

Cette interface vous permettra de:

- Ajouter de nouveaux produits à suivre
- Vérifier les prix actuels
- Visualiser les tendances de prix
- Générer des rapports
- Configurer des alertes

### Airflow avec Docker (méthode simplifiée)

1. Ouvrez une invite de commande dans le dossier du projet
2. Exécutez:
   ```
   .\airflow.bat
   ```
3. Accédez à l'interface web d'Airflow: http://localhost:8080
4. Connectez-vous avec les identifiants par défaut: admin / admin
5. Pour arrêter Airflow:
   ```
   .\airflow_stop.bat
   ```

### Tableau de bord de suivi des prix

Pour lancer le tableau de bord interactif:

1. Ouvrez une invite de commande dans le dossier du projet
2. Exécutez:
   ```
   .\start_dashboard.bat
   ```
3. Le tableau de bord s'ouvrira automatiquement dans votre navigateur à l'adresse: http://localhost:8050

## 🐳 Utilisation d'Airflow avec Docker

### Démarrer Airflow

1. Ouvrez une invite de commande ou PowerShell
2. Naviguez vers le dossier du projet: `cd c:\xampp\htdocs\Airflow`
3. Exécutez le script de démarrage: `.\airflow.bat`
4. Attendez que les conteneurs démarrent (environ 30-60 secondes)
5. Accédez à l'interface web: http://localhost:8080
6. Identifiants par défaut: admin / admin

### Vérifier l'état des conteneurs

```
docker ps --filter "name=airflow"
```

### Consulter les logs

```
docker logs airflow-webserver
docker logs airflow-scheduler
```

### Arrêter Airflow

```
docker-compose down
```

ou

```
.\airflow_stop.bat
```

### Réinitialiser complètement l'environnement

Si vous rencontrez des problèmes ou si vous souhaitez repartir de zéro:

```
.\airflow_rebuild.bat
```

## 📊 Tableau de bord

Le tableau de bord de suivi des prix offre une interface visuelle pour analyser les tendances et les variations de prix:

### Fonctionnalités du tableau de bord

- **Graphiques d'évolution des prix** : Visualisez les tendances sur différentes périodes
- **Statistiques de prix** : Min, max, moyenne et variation pour chaque produit
- **Alertes visuelles** : Notifications pour les prix bas ou en baisse significative
- **Filtres personnalisés** : Sélectionnez des produits et périodes spécifiques
- **Rafraîchissement automatique** : Mise à jour des données toutes les 5 minutes

### Démarrage du tableau de bord

```
.\start_dashboard.bat
```

Accédez au tableau de bord via: http://localhost:8050

## 📁 Structure du projet

```
Airflow/
├── airflow.bat               # Script de démarrage principal d'Airflow avec Docker
├── airflow_stop.bat          # Script pour arrêter Airflow proprement
├── airflow_rebuild.bat       # Script pour reconstruire les images Docker
├── airflow_tasks.py          # Interface interactive pour gérer Airflow
├── docker-compose.yml        # Configuration Docker pour Airflow
├── Dockerfile                # Configuration de l'image Docker personnalisée
├── start_dashboard.bat       # Script pour lancer le tableau de bord
├── dags/                     # Dossier contenant les DAGs Airflow
│   └── price_tracker_dag.py  # DAG principal pour le suivi des prix
├── scripts/                  # Scripts Python utilisés par les DAGs
│   ├── scraper.py            # Module de scraping des prix
│   ├── processor.py          # Traitement des données de prix
│   ├── visualizer.py         # Génération de graphiques et visualisations
│   ├── dashboard_improved.py # Tableau de bord Dash amélioré
│   └── save_price.py         # Sauvegarde des données de prix
├── plugins/                  # Plugins Airflow personnalisés
├── logs/                     # Logs générés par Airflow
├── data/                     # Données stockées (CSV des prix, etc.)
│   ├── prices.csv            # Historique des prix
│   └── products.json         # Configuration des produits suivis
├── price_tracking.py         # Interface utilisateur pour le suivi des prix
├── improved_dashboard.py     # Lanceur de tableau de bord avec gestion d'erreurs
├── clean_prices_data.py      # Utilitaire pour nettoyer les données de prix
└── requirements.txt          # Dépendances Python
```

## 📊 DAGs et scripts

### DAG de suivi des prix (`price_tracker_dag.py`)

Ce DAG principal automatise le processus de suivi des prix:

1. **Scraping des sites e-commerce** : Collecte les prix actuels
2. **Traitement des données** : Nettoyage et structuration
3. **Détection des baisses de prix** : Identification des opportunités
4. **Génération de rapports** : Création de visualisations
5. **Sauvegarde des données** : Archivage des historiques de prix

Le DAG s'exécute automatiquement toutes les 6 heures pour maintenir les données à jour.

### Scripts principaux

- **scraper.py** : Module qui extrait les prix des sites e-commerce avec gestion de cache et rotation des user-agents
- **processor.py** : Traite les données brutes et détecte les changements de prix
- **visualizer.py** : Génère des graphiques et des visualisations des tendances de prix
- **dashboard_improved.py** : Interface Dash pour la visualisation interactive des données
- **save_price.py** : Gère la sauvegarde et l'historisation des données de prix

## ❓ Dépannage

### Erreurs Docker

- **Docker ne démarre pas** : Vérifiez que Docker Desktop est en cours d'exécution
- **Erreur de port** : Assurez-vous que les ports 8080 (Airflow) et 8050 (Dashboard) ne sont pas utilisés
- **Conteneurs qui s'arrêtent** : Vérifiez les logs avec `docker logs airflow-webserver`

### Problèmes d'Airflow

- **DAGs non visibles** : Vérifiez la syntaxe du fichier DAG et redémarrez les conteneurs
- **Tâches en échec** : Consultez les logs de la tâche dans l'interface web d'Airflow
- **Erreurs d'importation Python** : Vérifiez que tous les modules nécessaires sont disponibles

### Problèmes de scraping

- **Échec du scraping** : Le site peut avoir changé sa structure ou bloqué les requêtes
- **Données manquantes** : Vérifiez les sélecteurs CSS dans la configuration des produits
- **Trop de requêtes** : Ajustez les délais entre les requêtes pour éviter d'être bloqué

### Problèmes de tableau de bord

- **Erreurs Dash** : Vérifiez que les dépendances (dash, plotly, pandas) sont installées
- **Données non affichées** : Assurez-vous que le fichier prices.csv existe et contient des données
- **Crash du tableau de bord** : Consultez les logs dans la console pour identifier l'erreur

## ☁️ Solutions cloud

Dans le cadre de l'optimisation et de la mise à l'échelle de ce projet, j'ai exploré plusieurs options cloud pour déployer le système de suivi des prix et Airflow :

### Options explorées

1. **AWS Managed Workflows for Apache Airflow (MWAA)** :

   - Service Airflow entièrement géré qui facilite la configuration et la maintenance
   - Intégration avec les autres services AWS (S3, RDS, Lambda)
   - Coûts prévisibles avec facturation à l'utilisation

2. **Google Cloud Composer** :

   - Service Airflow géré par Google Cloud
   - Intégration avec BigQuery pour l'analyse des données de prix
   - Évolutivité automatique en fonction de la charge

3. **Azure Data Factory avec Airflow** :

   - Intégration d'Airflow dans l'écosystème Azure
   - Possibilités d'analyse avancée avec Azure Synapse
   - Bonne intégration avec les services Power BI pour les tableaux de bord

4. **Solutions de conteneurs Kubernetes** :
   - Déploiement d'Airflow sur AKS, EKS ou GKE
   - Haute disponibilité et résilience
   - Contrôle précis sur l'infrastructure

### Avantages potentiels

- **Évolutivité** : Capacité à suivre un nombre beaucoup plus important de produits
- **Fiabilité** : Haute disponibilité et reprise après sinistre
- **Performances** : Ressources adaptées automatiquement à la charge
- **Sécurité** : Protection des données et conformité améliorées
- **Tableaux de bord avancés** : Intégration avec des outils d'analyse BI en cloud

### Prochaines étapes

La solution actuelle basée sur Docker fonctionne bien pour un usage personnel ou à petite échelle. Pour un déploiement en production ou à plus grande échelle, une migration vers une solution cloud pourrait être envisagée en fonction des besoins futurs et du budget disponible.

---

## 📜 Licence

Projet interne - Utilisation réservée.

---

Dernière mise à jour : 15 juin 2025

_Ce README regroupe toute la documentation sur Airflow avec Docker, le système de suivi des prix e-commerce et le tableau de bord interactif._
