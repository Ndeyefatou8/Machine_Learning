import dash
from dash import dcc, html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import pandas as pd
import geopandas as gpd  # Assurez-vous d'installer geopandas
#import dash_leaflet as dl
import plotly.express as px
from cachetools import cached


# Chargez le fichier CSS
external_stylesheets = ['styles.css']  # Remplacez 'styles.css' par le nom de votre fichier CSS

# Charger les données géographiques de la France
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))

#url git
url = 'https://github.com/Pioterr/projet_sise_stock/blob/main/concat.zip?raw=true'

# Chargez le fichier CSV
#df = pd.read_csv(filepath_or_buffer= url ,sep='|', compression='zip')
#print(df.columns)

@cached(maxsize=10)
def get_df():
    """Charge le df à partir du disque et le stocke dans la mémoire vive."""
    return pd.read_csv(filepath_or_buffer= url ,sep='|', compression='zip')

# Utilisez la fonction get_df() pour obtenir le df
df = get_df()
# Obtenez les valeurs uniques de la colonne "commune"
commune_options = [{'label': commune, 'value': commune} for commune in df['Commune'].unique()]
# Filtrez la géométrie de la France
france = world[world['name'] == 'France']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

#TEST
# Créez un exemple de données pour la courbe d'évolution (remplacez par vos données réelles)
annees = [2010, 2011, 2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020]
prix_metre_carre = [2000, 2200, 2350, 2400, 2500, 2600, 2700, 2800, 2900, 3000, 3100]

## CE QU'IL FAIRE
#prix_metre_carre = df.groupby('Annee')['PrixM2'].mean().reset_index()  # Remplacez 'Annee' et 'PrixM2' par les noms de colonnes de votre DataFrame
#courbe_evolution = dcc.Graph(figure=px.line(prix_metre_carre, x='Annee', y='PrixM2', labels={'Annee': 'Années', 'PrixM2': 'Prix du mètre carré'}, title='Évolution du Prix du Mètre Carré'))

# Créez le graphique d'évolution
courbe_evolution = dcc.Graph(figure=px.line(x=annees, y=prix_metre_carre, labels={'x': 'Années', 'y': 'Prix du mètre carré'}, title='Évolution du Prix du Mètre Carré'))

# Créez la carte de la France
fig = px.choropleth(france, 
                    locations='iso_a3',
                    color='pop_est',
                    hover_name='name',
                    color_continuous_scale=px.colors.sequential.Plasma)


# Créez une barre latérale pour les filtres
sidebar = dbc.Container([
    dbc.Col([
        html.H2("Filtres"),
        dbc.CardGroup([
            dbc.Label("Filtrer par commune"),
            dcc.Dropdown(id='commune-dropdown', options=commune_options, value=commune_options[0]['value'], style={'width': '90%', 'margin-bottom': '10px'})
        ]),
        dbc.CardGroup([
            dbc.Label("Filtrer par surface en m²"),
            dcc.Input(id='surface-input', type='number', placeholder='Surface en m²',style={'margin-bottom': '10px'})
        ]),
        dbc.Button("Rechercher", id='search-button', n_clicks=0)
    ],width= 10, style={'background-color': 'white', 'padding': '20px', 'height': '100vh','margin-bottom': '20px'})
], className='sidebar')


# Créez une zone principale pour afficher le graphique
main_content = dbc.Container([
    dbc.Col([
        dcc.Graph(figure=fig, id='map-plot')
    ])
], className='main-content', style={'margin-top': '40px'})

# Créez une mise en page avec la barre latérale et la zone principale
app.layout = html.Div([
   html.H1("Estimation des Prix Immobiliers", style={'text-align': 'center','color': 'white'}),
    dcc.Tabs(id='tabs', value='onglet-1', children=[
        dcc.Tab(label='Cartographie', value='onglet-1'),
        dcc.Tab(label='Prédiction prix de vente', value='onglet-2'),
        dcc.Tab(label='Évolution', value='onglet-3'),
    ]),
    dbc.Row([
        dbc.Col(sidebar, width=3),
        dbc.Col([
            html.Div(main_content, id='content-onglet-1', style={'display': 'block'}),
            html.Div("Contenu de l'onglet 2", id='content-onglet-2', style={'display': 'none'}),
            html.Div(courbe_evolution, id='content-onglet-3', style={'display': 'none'}),
        ], width=9)

        
    ])
])

# Gérez la navigation entre les onglets
@app.callback(
    Output('content-onglet-1', 'style'),
    Output('content-onglet-2', 'style'),
    Output('content-onglet-3', 'style'),
    [Input('tabs', 'value')]
)
def display_content(tab):
    if tab == 'onglet-1':
        return {'display': 'block'}, {'display': 'none'}, {'display': 'none'}
    elif tab == 'onglet-2':
        return {'display': 'none'}, {'display': 'block'}, {'display': 'none'}
    elif tab == 'onglet-3':
        return {'display': 'none'}, {'display': 'none'}, {'display': 'block'}



if __name__ == '__main__':
    app.run_server(debug=True)

