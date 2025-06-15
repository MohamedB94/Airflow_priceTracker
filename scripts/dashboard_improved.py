import os
import sys
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import traceback

# Définition des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PRICES_CSV = os.path.join(DATA_DIR, 'prices.csv')
PRODUCTS_JSON = os.path.join(DATA_DIR, 'products.json')

# Vérifier l'existence des fichiers de données
def verify_data_files():
    missing_files = []
    if not os.path.exists(PRICES_CSV):
        # Créer un fichier vide avec en-têtes si inexistant
        try:
            os.makedirs(DATA_DIR, exist_ok=True)
            with open(PRICES_CSV, 'w') as f:
                f.write("product_id,product_name,price,currency,date\n")
            print(f"Fichier créé: {PRICES_CSV}")
        except Exception as e:
            missing_files.append(f"prices.csv (Erreur: {str(e)})")
    
    if not os.path.exists(PRODUCTS_JSON):
        missing_files.append("products.json")
    
    return missing_files

missing_files = verify_data_files()
if missing_files:
    print("AVERTISSEMENT: Certains fichiers de données sont manquants:")
    for file in missing_files:
        print(f" - {file}")
    print("Le tableau de bord pourrait ne pas fonctionner correctement.")

# Fonction pour charger les données de prix de manière sécurisée
def load_price_data():
    try:
        if os.path.exists(PRICES_CSV) and os.path.getsize(PRICES_CSV) > 0:
            df = pd.read_csv(PRICES_CSV)
            # Convertir la colonne date en datetime
            df['date'] = pd.to_datetime(df['date'])
            return df
        else:
            print(f"Le fichier {PRICES_CSV} est vide ou n'existe pas.")
            # Retourner un DataFrame vide avec les colonnes attendues
            return pd.DataFrame(columns=['product_id', 'product_name', 'price', 'currency', 'date'])
    except Exception as e:
        print(f"Erreur lors du chargement des données de prix: {str(e)}")
        traceback.print_exc()
        # Retourner un DataFrame vide avec les colonnes attendues
        return pd.DataFrame(columns=['product_id', 'product_name', 'price', 'currency', 'date'])

# Fonction pour charger les données de produits de manière sécurisée
def load_product_data():
    try:
        import json
        if os.path.exists(PRODUCTS_JSON) and os.path.getsize(PRODUCTS_JSON) > 0:
            with open(PRODUCTS_JSON, 'r') as f:
                products = json.load(f)
            return products
        else:
            print(f"Le fichier {PRODUCTS_JSON} est vide ou n'existe pas.")
            return []
    except Exception as e:
        print(f"Erreur lors du chargement des données de produits: {str(e)}")
        traceback.print_exc()
        return []

# Initialisation de l'application Dash
app = dash.Dash(__name__, title='Suivi des Prix E-Commerce')

# Définition de la mise en page de l'application
app.layout = html.Div(
    style={'font-family': 'Arial, sans-serif', 'margin': '0', 'padding': '20px', 'background-color': '#f5f5f5'},
    children=[
        html.H1('Tableau de Bord de Suivi des Prix E-Commerce', 
                style={'textAlign': 'center', 'color': '#2c3e50', 'margin-bottom': '30px'}),
        
        html.Div([
            html.Div([
                html.Label('Sélectionner la Période:'),
                dcc.Dropdown(
                    id='time-range-dropdown',
                    options=[
                        {'label': 'Derniers 7 jours', 'value': '7'},
                        {'label': 'Derniers 30 jours', 'value': '30'},
                        {'label': 'Derniers 90 jours', 'value': '90'},
                        {'label': 'Tout', 'value': 'all'}
                    ],
                    value='30',
                    style={'width': '100%'}
                ),
            ], style={'width': '30%', 'display': 'inline-block', 'margin-right': '20px'}),
            
            html.Div([
                html.Label('Sélectionner les Produits:'),
                dcc.Dropdown(
                    id='product-dropdown',
                    multi=True,
                    style={'width': '100%'}
                ),
            ], style={'width': '60%', 'display': 'inline-block'}),
        ], style={'margin-bottom': '20px'}),
        
        html.Div([
            html.Div([
                dcc.Graph(id='price-history-graph')
            ], style={'width': '70%', 'display': 'inline-block', 'vertical-align': 'top'}),
            
            html.Div([
                html.H3('Alertes de Prix', style={'textAlign': 'center', 'color': '#2c3e50'}),
                html.Div(id='price-alerts', style={'padding': '10px'})
            ], style={'width': '28%', 'display': 'inline-block', 'margin-left': '2%', 'background-color': 'white', 'border-radius': '5px', 'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'}),
        ]),
        
        html.Div([
            html.H3('Tableau des Prix', style={'textAlign': 'center', 'color': '#2c3e50', 'margin-top': '30px'}),
            html.Div(id='price-table')
        ]),
        
        # Intervalle pour mise à jour automatique
        dcc.Interval(
            id='interval-component',
            interval=300*1000,  # en millisecondes (5 minutes)
            n_intervals=0
        ),
        
        # Information sur l'état du système
        html.Div([
            html.Hr(),
            html.P(f"Données chargées depuis {PRICES_CSV}", style={'color': 'gray', 'font-size': '12px'}),
            html.P(f"Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", id='last-update-time', style={'color': 'gray', 'font-size': '12px'}),
            html.P("Le tableau de bord se rafraîchit automatiquement toutes les 5 minutes", style={'color': 'gray', 'font-size': '12px'}),
        ], style={'margin-top': '40px', 'text-align': 'center'})
    ]
)

# Callback pour mettre à jour la liste déroulante des produits
@app.callback(
    Output('product-dropdown', 'options'),
    Output('product-dropdown', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_product_dropdown(n):
    try:
        df = load_price_data()
        if df.empty:
            return [], []
            
        # Obtenir la liste unique des produits avec leurs IDs
        products = df[['product_id', 'product_name']].drop_duplicates()
        options = [{'label': row['product_name'], 'value': row['product_id']} for _, row in products.iterrows()]
        
        # Sélectionner par défaut tous les produits
        default_values = [option['value'] for option in options]
        
        return options, default_values
    except Exception as e:
        print(f"Erreur lors de la mise à jour de la liste déroulante des produits: {str(e)}")
        traceback.print_exc()
        return [], []

# Callback pour mettre à jour le graphique d'historique des prix
@app.callback(
    Output('price-history-graph', 'figure'),
    Input('product-dropdown', 'value'),
    Input('time-range-dropdown', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_price_history(selected_products, time_range, n):
    try:
        df = load_price_data()
        if df.empty or not selected_products:
            # Retourner un graphique vide
            return {
                'data': [],
                'layout': {
                    'title': 'Aucune donnée disponible',
                    'xaxis': {'title': 'Date'},
                    'yaxis': {'title': 'Prix'}
                }
            }
        
        # Filtrer par produits sélectionnés
        df = df[df['product_id'].isin(selected_products)]
        
        # Filtrer par plage de temps
        if time_range != 'all':
            end_date = datetime.now()
            start_date = end_date - timedelta(days=int(time_range))
            df = df[df['date'] >= start_date]
        
        # Créer le graphique
        fig = px.line(df, x='date', y='price', color='product_name', 
                      title='Évolution des Prix',
                      labels={'date': 'Date', 'price': 'Prix', 'product_name': 'Produit'})
        
        fig.update_layout(
            xaxis_title='Date',
            yaxis_title='Prix (€)',
            legend_title='Produits',
            hovermode='closest',
            template='plotly_white'
        )
        
        return fig
    except Exception as e:
        print(f"Erreur lors de la mise à jour du graphique d'historique des prix: {str(e)}")
        traceback.print_exc()
        return {
            'data': [],
            'layout': {
                'title': f'Erreur lors de la génération du graphique: {str(e)}',
                'xaxis': {'title': 'Date'},
                'yaxis': {'title': 'Prix'}
            }
        }

# Callback pour mettre à jour le tableau des prix
@app.callback(
    Output('price-table', 'children'),
    Input('product-dropdown', 'value'),
    Input('interval-component', 'n_intervals')
)
def update_price_table(selected_products, n):
    try:
        df = load_price_data()
        if df.empty or not selected_products:
            return html.P("Aucune donnée disponible")
        
        # Filtrer par produits sélectionnés
        df = df[df['product_id'].isin(selected_products)]
        
        # Obtenir les derniers prix pour chaque produit
        latest_prices = []
        for product_id in selected_products:
            product_data = df[df['product_id'] == product_id]
            if not product_data.empty:
                latest_price = product_data.sort_values('date', ascending=False).iloc[0]
                latest_prices.append({
                    'product_name': latest_price['product_name'],
                    'price': latest_price['price'],
                    'currency': latest_price['currency'],
                    'date': latest_price['date'].strftime('%Y-%m-%d %H:%M')
                })
        
        if not latest_prices:
            return html.P("Aucune donnée de prix disponible pour les produits sélectionnés")
        
        # Créer le tableau
        header = html.Tr([
            html.Th('Produit', style={'textAlign': 'left', 'padding': '10px'}),
            html.Th('Prix Actuel', style={'textAlign': 'right', 'padding': '10px'}),
            html.Th('Dernière Mise à Jour', style={'textAlign': 'center', 'padding': '10px'})
        ])
        
        rows = []
        for price_data in latest_prices:
            row = html.Tr([
                html.Td(price_data['product_name'], style={'textAlign': 'left', 'padding': '10px'}),
                html.Td(f"{price_data['price']:.2f} {price_data['currency']}", style={'textAlign': 'right', 'padding': '10px'}),
                html.Td(price_data['date'], style={'textAlign': 'center', 'padding': '10px'})
            ])
            rows.append(row)
        
        table = html.Table([
            html.Thead(header),
            html.Tbody(rows)
        ], style={'width': '100%', 'border-collapse': 'collapse', 'box-shadow': '0 4px 6px rgba(0, 0, 0, 0.1)'})
        
        return table
    except Exception as e:
        print(f"Erreur lors de la mise à jour du tableau des prix: {str(e)}")
        traceback.print_exc()
        return html.P(f"Erreur lors de la génération du tableau: {str(e)}")

# Callback pour mettre à jour les alertes de prix
@app.callback(
    Output('price-alerts', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_price_alerts(n):
    try:
        df = load_price_data()
        products = load_product_data()
        
        if df.empty or not products:
            return html.P("Aucune donnée disponible pour générer des alertes")
        
        alerts_list = []
        
        for product in products:
            product_id = product.get('id')
            product_name = product.get('name')
            threshold_price = product.get('threshold_price')
            notify_on_drop = product.get('notify_on_drop', False)
            
            product_data = df[df['product_id'] == product_id].sort_values('date', ascending=False)
            
            if product_data.empty:
                continue
                
            latest_price = product_data.iloc[0]['price']
            
            # Vérifier s'il y a au moins deux points de données pour comparer
            if len(product_data) > 1:
                previous_price = product_data.iloc[1]['price']
                price_change = latest_price - previous_price
                
                alert_message = None
                alert_color = None
                
                # Alerte de baisse de prix
                if price_change < 0 and notify_on_drop:
                    alert_message = f"Prix baissé de {abs(price_change):.2f} € ! Maintenant à {latest_price:.2f} €"
                    alert_color = "#4caf50"  # Vert
                
                # Alerte de seuil de prix
                elif threshold_price and latest_price <= threshold_price:
                    alert_message = f"Prix inférieur au seuil de {threshold_price:.2f} € ! Actuellement à {latest_price:.2f} €"
                    alert_color = "#2196f3"  # Bleu
                
                if alert_message:
                    alert_card = html.Div([
                        html.H4(product_name, style={'margin-bottom': '5px'}),
                        html.P(alert_message),
                    ], style={'margin-bottom': '15px', 'padding': '10px', 'border-left': f'4px solid {alert_color}', 'background-color': '#f9f9f9'})
                    
                    alerts_list.append(alert_card)
        
        if not alerts_list:
            return html.P("Aucune alerte de prix pour le moment")
        
        return alerts_list
    except Exception as e:
        print(f"Erreur lors de la mise à jour des alertes de prix: {str(e)}")
        traceback.print_exc()
        return html.P(f"Erreur: {str(e)}")

# Callback pour mettre à jour l'heure de dernière mise à jour
@app.callback(
    Output('last-update-time', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_last_update_time(n):
    return f"Dernière mise à jour: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"

# Run the app
if __name__ == '__main__':
    print("Démarrage du tableau de bord Dash sur http://0.0.0.0:8050")
    print("Maintenez ce processus actif pour continuer à accéder au tableau de bord.")
    app.run(debug=False, host='0.0.0.0', port=8050)
