import os
import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Définition des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PRICES_CSV = os.path.join(DATA_DIR, 'prices.csv')
PRODUCTS_CSV = os.path.join(DATA_DIR, 'products.csv')

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
            dcc.Graph(id='price-trend-graph'),
        ], style={'padding': '20px', 'background-color': 'white', 'box-shadow': '0px 0px 10px rgba(0,0,0,0.1)', 'border-radius': '5px'}),
        
        html.Div([
            html.Div([
                html.H3('Statistiques des Prix', style={'textAlign': 'center'}),
                html.Div(id='price-stats'),
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '15px', 'background-color': 'white', 'box-shadow': '0px 0px 10px rgba(0,0,0,0.1)', 'border-radius': '5px', 'margin-right': '2%'}),
            
            html.Div([
                html.H3('Alertes de Prix', style={'textAlign': 'center'}),
                html.Div(id='price-alerts'),
            ], style={'width': '48%', 'display': 'inline-block', 'padding': '15px', 'background-color': 'white', 'box-shadow': '0px 0px 10px rgba(0,0,0,0.1)', 'border-radius': '5px'}),
        ], style={'margin-top': '20px', 'display': 'flex'}),
        
        html.Div([
            html.P('Dernière mise à jour: ' + datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 
                   id='last-updated', 
                   style={'textAlign': 'right', 'margin-top': '20px', 'font-style': 'italic', 'color': '#7f8c8d'})
        ]),
    ]
)

# Fonction auxiliaire pour charger les données
def load_data():
    try:
        prices_df = pd.read_csv(PRICES_CSV)
        products_df = pd.read_csv(PRODUCTS_CSV)
        
        # Convertit la colonne date en datetime
        prices_df['date'] = pd.to_datetime(prices_df['date'])
        
        # Fusionne avec les données produit pour obtenir les noms
        df = pd.merge(
            prices_df, 
            products_df[['product_id', 'title']], 
            on='product_id', 
            how='left'
        )
        
        return df, products_df
    except Exception as e:
        print(f"Erreur lors du chargement des données: {e}")
        return pd.DataFrame(), pd.DataFrame()

# Callback to update product dropdown options
@app.callback(
    Output('product-dropdown', 'options'),
    Output('product-dropdown', 'value'),
    Input('time-range-dropdown', 'value')  # Dummy input to trigger on page load
)
def update_product_dropdown(dummy):
    try:
        _, products_df = load_data()
        options = [{'label': row['title'], 'value': row['product_id']} 
                   for _, row in products_df.iterrows()]
        all_products = [product['value'] for product in options]
        return options, all_products
    except Exception as e:
        print(f"Error updating product dropdown: {e}")
        return [], []

# Callback to update price trend graph
@app.callback(
    Output('price-trend-graph', 'figure'),
    Input('time-range-dropdown', 'value'),
    Input('product-dropdown', 'value')
)
def update_price_trend(time_range, selected_products):
    try:
        df, _ = load_data()
        
        if df.empty:
            return go.Figure().update_layout(title="No data available")
        
        # Filter by time range
        if time_range != 'all':
            days = int(time_range)
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df['date'] >= cutoff_date]
        
        # Filter by selected products
        if selected_products:
            df = df[df['product_id'].isin(selected_products)]
        
        # Create the figure
        fig = px.line(
            df, 
            x='date', 
            y='price', 
            color='title',
            markers=True,
            title=f'Price Trends - {time_range if time_range != "all" else "All Time"}',
            labels={'date': 'Date', 'price': 'Price', 'title': 'Product'}
        )
        
        # Update layout
        fig.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=20, r=20, t=50, b=20),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
            xaxis=dict(
                title='Date',
                gridcolor='lightgray',
                zeroline=False
            ),
            yaxis=dict(
                title='Price',
                gridcolor='lightgray',
                zeroline=False
            ),
            font=dict(family='Arial', size=12)
        )
        
        return fig
    except Exception as e:
        print(f"Error updating price trend graph: {e}")
        return go.Figure().update_layout(title=f"Error: {str(e)}")

# Callback to update price statistics
@app.callback(
    Output('price-stats', 'children'),
    Input('product-dropdown', 'value'),
    Input('time-range-dropdown', 'value')
)
def update_price_stats(selected_products, time_range):
    try:
        df, products_df = load_data()
        
        if df.empty or not selected_products:
            return html.P("No data available")
        
        # Filter by time range
        if time_range != 'all':
            days = int(time_range)
            cutoff_date = datetime.now() - timedelta(days=days)
            df = df[df['date'] >= cutoff_date]
        
        # Filter by selected products
        df = df[df['product_id'].isin(selected_products)]
        
        stats_list = []
        for product_id in selected_products:
            product_df = df[df['product_id'] == product_id]
            if product_df.empty:
                continue
                
            product_name = product_df['title'].iloc[0]
            
            # Calculate statistics
            current_price = product_df.iloc[-1]['price']
            min_price = product_df['price'].min()
            max_price = product_df['price'].max()
            avg_price = product_df['price'].mean()
            
            # Calculate price change
            if len(product_df) > 1:
                first_price = product_df.iloc[0]['price']
                price_change = current_price - first_price
                price_change_pct = (price_change / first_price) * 100
                price_trend = 'Up' if price_change > 0 else 'Down' if price_change < 0 else 'Stable'
                price_trend_color = '#e74c3c' if price_change > 0 else '#2ecc71' if price_change < 0 else '#3498db'
            else:
                price_change = 0
                price_change_pct = 0
                price_trend = 'Stable'
                price_trend_color = '#3498db'
            
            # Create stats card
            stats_card = html.Div([
                html.H4(product_name, style={'margin-bottom': '10px'}),
                html.Div([
                    html.Span('Current: ', style={'font-weight': 'bold'}),
                    html.Span(f'{current_price:.2f}'),
                ]),
                html.Div([
                    html.Span('Min: ', style={'font-weight': 'bold'}),
                    html.Span(f'{min_price:.2f}'),
                ]),
                html.Div([
                    html.Span('Max: ', style={'font-weight': 'bold'}),
                    html.Span(f'{max_price:.2f}'),
                ]),
                html.Div([
                    html.Span('Avg: ', style={'font-weight': 'bold'}),
                    html.Span(f'{avg_price:.2f}'),
                ]),
                html.Div([
                    html.Span('Trend: ', style={'font-weight': 'bold'}),
                    html.Span(f'{price_trend} ({price_change_pct:.2f}%)', style={'color': price_trend_color}),
                ]),
            ], style={'margin-bottom': '15px', 'padding': '10px', 'border-left': f'4px solid {price_trend_color}', 'background-color': '#f9f9f9'})
            
            stats_list.append(stats_card)
        
        if not stats_list:
            return html.P("No statistics available for selected products and time range")
        
        return stats_list
    except Exception as e:
        print(f"Error updating price stats: {e}")
        return html.P(f"Error: {str(e)}")

# Callback to update price alerts
@app.callback(
    Output('price-alerts', 'children'),
    Input('product-dropdown', 'value')
)
def update_price_alerts(selected_products):
    try:
        df, products_df = load_data()
        
        if df.empty or not selected_products:
            return html.P("No products selected")
        
        alerts_list = []
        for product_id in selected_products:
            # Get product info
            product_info = products_df[products_df['product_id'] == product_id]
            if product_info.empty:
                continue
                
            product_name = product_info['title'].iloc[0]
            threshold_price = product_info['threshold_price'].iloc[0] if 'threshold_price' in product_info.columns else None
            
            # Get price history
            product_df = df[df['product_id'] == product_id].sort_values('date')
            if product_df.empty:
                continue
                
            current_price = product_df.iloc[-1]['price']
            
            # Check for price drops
            if len(product_df) > 1:
                previous_prices = product_df.iloc[:-1]['price'].tolist()
                min_previous = min(previous_prices) if previous_prices else current_price
                
                # Create alert card
                alert_message = None
                alert_color = '#3498db'
                
                if current_price < min_previous:
                    alert_message = f"Lowest price yet! Down from {min_previous:.2f} to {current_price:.2f}"
                    alert_color = '#2ecc71'
                elif threshold_price and current_price <= threshold_price:
                    alert_message = f"Below threshold! Current: {current_price:.2f}, Threshold: {threshold_price:.2f}"
                    alert_color = '#f39c12'
                
                if alert_message:
                    alert_card = html.Div([
                        html.H4(product_name, style={'margin-bottom': '5px'}),
                        html.P(alert_message),
                    ], style={'margin-bottom': '15px', 'padding': '10px', 'border-left': f'4px solid {alert_color}', 'background-color': '#f9f9f9'})
                    
                    alerts_list.append(alert_card)
        
        if not alerts_list:
            return html.P("No price alerts at this time")
        
        return alerts_list
    except Exception as e:
        print(f"Error updating price alerts: {e}")
        return html.P(f"Error: {str(e)}")

# Run the app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8050)
