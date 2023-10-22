import dash
from dash import dcc, html
#import dash_daq as daq
import plotly.graph_objects as go
import pandas as pd
from dash.dependencies import Input, Output,State
import dash_core_components as dcc
import plotly.express as px
import dash_bootstrap_components as dbc  # Importez dbc
import geopandas as gpd
import joblib 
import requests
from sklearn.preprocessing import LabelEncoder
import certifi
#import dash_daq as daq


# Chargez le fichier CSS
external_stylesheets = ['https://github.com/Ndeyefatou8/Machine_Learning/blob/main/style.css']  


# Chargez les données depuis GitHub
url_df_prix = 'https://github.com/Ndeyefatou8/Machine_Learning/blob/main/echantillon.csv?raw=true'
url_carte_dep = 'https://github.com/Ndeyefatou8/Machine_Learning/blob/branche_Albane/carte%2B.zip?raw=true'
url_moy_dep_l_2021 = 'https://github.com/Ndeyefatou8/Machine_Learning/blob/branche-pierre/moy_departement_locaux_2021.csv?raw=true'
url_moy_dep_d_2021 = 'https://github.com/Ndeyefatou8/Machine_Learning/blob/branche-pierre/moy_departement_dependance_2021.csv?raw=true'
url_prix_m2_com_region = 'https://github.com/Ndeyefatou8/Machine_Learning/blob/branche_Fatou/prix_m2_com_region.csv?raw=true'
# Spécifiez les URL bruts des modèles
url_model_maison = 'https://github.com/Ndeyefatou8/Machine_Learning/blob/branche-pierre/reg_prix_maison.pkl?raw=true'
url_model_appart = 'https://github.com/Ndeyefatou8/Machine_Learning/blob/branche-pierre/reg_prix_appart.pkl?raw=true'

#url_model_maison='https://github.com/Ndeyefatou8/Machine_Learning/blob/branche-pierre/reg_prix_maison.pkl?raw=true'
#url_model_appart='https://github.com/Ndeyefatou8/Machine_Learning/blob/branche-pierre/reg_prix_appart.pkl?raw=true'


df_prix = pd.read_csv(url_df_prix, sep=',')
carte_dep = pd.read_csv(filepath_or_buffer=url_carte_dep, sep=',', compression='zip')
moy_dep_l_2021 = pd.read_csv(filepath_or_buffer=url_moy_dep_l_2021, sep='|')
moy_dep_d_2021 = pd.read_csv(filepath_or_buffer=url_moy_dep_d_2021, sep='|')
prix_m2_com_region = pd.read_csv(filepath_or_buffer=url_prix_m2_com_region, sep=',')



response_prix_model_maison = requests.get(url_model_maison,verify=False)
response_prix_model_appart = requests.get(url_model_appart,verify=False)

with open('reg_prix_maison.pkl', 'wb') as f:
    f.write(response_prix_model_maison.content)
with open('reg_prix_appart.pkl', 'wb') as f:
    f.write(response_prix_model_appart.content)
prix_model_maison = joblib.load('reg_prix_maison.pkl')
prix_model_appart = joblib.load('reg_prix_appart.pkl')


# Créez un échantillon de 1000 lignes
#df2 = df.sample(n=1000,random_state=42)  
# Créez un cache avec une taille maximale de 10 éléments
#my_cache = cachetools.LRUCache(maxsize=10)
#@cached(my_cache)
#def get_df():
    #Charge le df à partir du disque et le stocke dans la mémoire vive
   #return pd.read_csv('C:/Users/HP/Desktop/Master2-SISE/Machine-Learning/Dash/concat/concat.csv',sep='|')
 #  return pd.read_csv(url ,sep='|', compression='zip')
# Utilisez la fonction get_df() pour obtenir le df
#df = get_df()


# Obtenez les valeurs uniques de la colonne "commune"
commune_options = [{'label': commune, 'value': commune} for commune in df2['Commune'].unique()]
#  les valeurs uniques de la colonne "commune"
region_options = [{'label': region, 'value': region} for region in df_prix['Code departement'].unique()]
# les valeurs uniques de la colonne "Type local" depuis votre jeu de données
type_local_options = [{'label': type_local, 'value': type_local} for type_local in df_prix['Type local'].unique()]


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],suppress_callback_exceptions=True)
server = app.server 



# Définissez la page d'accueil
page_daccueil = dbc.Container([
    dbc.Row([
        dbc.Col([
            html.Img(src="https://www.dynamique-mag.com/wp-content/uploads/rente-immobilier-780x470.jpeg", width="100%")
        ], width=6),
        dbc.Col([
            html.H2("À Propos"),
            html.P("Bienvenue sur notre application de prédiction des prix immobiliers. Cette application vous permet d'explorer les données de valeurs foncières et de prédire les prix immobiliers à l'aide de modèles de machine learning avancés. Vous pouvez utiliser les onglets ci-dessus pour accéder à différentes fonctionnalités.")
        ], width=6)
        
    ])
], className='main-content', style={'margin-top': '30px'})
# Créez une barre latérale pour les filtres
# Créez la barre latérale
sidebar = dbc.Container([
    dbc.Col([
        html.H2("Filtres"),
        dbc.CardGroup([
            dbc.Label("Filtrer par commune"),
            dcc.Checklist(id='commune-checklist', options=commune_options, value=[]),
        ]),
        dbc.CardGroup([
            dbc.Label("Filtrer par surface en m²"),
            dcc.Input(id='surface-input', type='number', placeholder='Surface en m²'),
        ]),
        dbc.Button("Rechercher", id='search-button', n_clicks=0)
    ],width= 10, style={'background-color': 'lightgray', 'padding': '20px', 'height': '100vh','margin-bottom': '20px'})
], className='sidebar')


# Créez une zone principale pour afficher le graphique
main_content = dbc.Container([
    dbc.Col([
        dcc.Graph(figure=fig, id='map-plot')
    ])
],className='main-content', style={'margin-top': '2 0px'})

#  section pour la prédiction du prix de vente

prediction_section = html.Div([
    html.H2("Prédiction du Prix de Vente"),
    dcc.Input(id='input-surface', type='number', placeholder='Entrez la surface (m²)', style={'width': '40%'}),
    dcc.Dropdown(id='input-region', options=region_options, placeholder='Sélectionnez la région', style={'width': '50%', 'margin-top': '10px'}),
    dcc.Dropdown(id='input-commune', options=commune_options, placeholder='Sélectionnez la commune', style={'width': '50%', 'margin-top': '10px'}),
    dcc.Dropdown(id='input-type-local', options=type_local_options, placeholder='Sélectionnez le type local', style={'width': '50%', 'margin-top': '10px'}),
    dbc.Button("Rechercher", id='predict-button', n_clicks=0),
    html.Div(id='prediction-output',children=[], style={'margin-top': '20px', 'border': '1px solid #ccc', 'padding': '10px', 'border-radius': '5px', 'height': '100px'})

])


# Créez la mise en page avec les onglets
app.layout = html.Div([
    html.H1("Estimation des Prix Immobiliers", className="app-title"),
    dcc.Tabs(id='tabs', value='onglet-0', children=[
        dcc.Tab(label='Accueil', value='onglet-0'),
        dcc.Tab(label='Cartographie', value='onglet-1'),
        dcc.Tab(label='Prédiction prix de vente', value='onglet-2'),
        dcc.Tab(label='Évolution', value='onglet-3'),
    ], className='app-header'),
    html.Div(id='content')
])


# Callback pour mettre à jour le graphique en fonction de la sélection des communes
@app.callback(
    Output('commune-price-evolution-graph', 'figure'),
    Input('commune-dropdown', 'value')
)
def update_commune_price_evolution(selected_communes):
    if not selected_communes:
         # Si aucune commune sélectionnée, utilisez la première ville par défaut
        selected_communes = [df_prix['Commune'].unique()[0]]
    # Filtrez les données en fonction des communes sélectionnées
    filtered_data = df_prix[df_prix['Commune'].isin(selected_communes)]

    # Créez le graphique d'évolution pour les communes
    fig = px.line(filtered_data, x='year', y='Prix m2 moyen commune', color='Commune', title='Évolution du Prix du Mètre Carré par Commune')

    return fig

@app.callback(
    Output('region-price-evolution-graph', 'figure'),
    Input('depart-dropdown', 'value')
)
def update_region_price_evolution(selected_depart):
    if not selected_depart:
        # Si aucune commune sélectionnée, utilisez la première ville par défaut
        selected_depart= [df_prix['Code departement'].unique()[0]]

    # Filtrez les données en fonction des communes sélectionnées
    data_depart = df_prix[df_prix['Code departement'].isin(selected_depart)]
    
    
    # Créez le graphique d'évolution pour les communes
    fig = px.line(data_depart, x='year', y='Prix m2 moyen region', color='Code departement', title='Évolution du Prix du Mètre Carré par Region  {}'.format(selected_depart))

    # Créez le diagramme circulaire du prix moyen groupé par type local
    #fig = px.pie(data_depart, names='Type local', values='Prix m2 moyen region',
     #            title='Prix Moyen par Type Local pour la Commune {}'.format(selected_depart))
    return fig

@app.callback(
    Output('typelocal-price-evolution-diagr', 'figure'),
    Input('typelocal-dropdown', 'value'))
#TYPE LOCAL
def update_typelocal_price_evolution(selected_communes):
    if not selected_communes:
        # Si aucune commune sélectionnée, utilisez la première ville par défaut
        selected_communes = [df_prix ['Commune'].unique()[0]]

    # Filtrez les données en fonction des communes sélectionnées
    filtered_data = df_prix [df_prix ['Commune'].isin(selected_communes)]
    
    # Créez le barplot du prix moyen par type local
    fig = px.histogram(filtered_data, x='Type local', y='Prix m2 moyen commune',color='Commune',
                 title='Prix Moyen par Type Local par Commune {}'.format(selected_communes))

    return fig
    
#CARTOGRAPHIE
carte = px.scatter_mapbox(carte_dep, lat="latitude", lon="longitude", hover_name="Commune", color="Code departement",hover_data=["Prix m2 moyen region", "Prix m2 moyen commune"], zoom=6, height=600)
carte.update_layout(mapbox_style="open-street-map")
carte.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
    
 
 #PREDICTON 

# Callback pour la prédiction
@app.callback(
    Output("prediction-output", "children"),
    Input("predict-button", "n_clicks"),
    State("input-surface", "value"),
    State("input-region", "value"),
    State("input-commune", "value"),
    State("input-type-local", "value")
)
def prediction(n_clicks, Surface, region, commune, Type_loc):
    if n_clicks is not None:
        if Surface is None or region is None or commune is None or Type_loc is None:
            return "Veuillez remplir toutes les informations du formulaire."
        else:
            # Votre code de prédiction ici
            Surface=int(Surface)
            region=str(region)
            commune=str(commune)
            Type_loc=str(Type_loc)
            
            prix_m2 = prix_m2_com_region[(prix_m2_com_region['Commune'] == commune) & (prix_m2_com_region['Code departement'] == region)]['Prix m2 moyen commune']
           
            df = pd.DataFrame({'Surface reelle bati': Surface, 'Prix m2 moyen commune': prix_m2})
            if Type_loc == 'Maison':
                result = pd.DataFrame(prix_model_maison.predict(df)).iloc[0]

            elif Type_loc == 'Appartement':
                result = pd.DataFrame(prix_model_appart.predict(df)).iloc[0]
            elif Type_loc == 'Dépendance':
                result = moy_dep_d_2021[moy_dep_d_2021['Code departement'] == region]['Valeur fonciere']
            else:
                result = moy_dep_l_2021[moy_dep_l_2021['Code departement'] == region]['Valeur fonciere']+ 10000
            return f"Le prix estimé est de {result.iloc[0]:.2f} €."
    else:
        return ""

# Gérez la navigation entre les onglets
@app.callback(
    Output('content', 'children'),
    [Input('tabs', 'value')]
)
def display_content(tab):
    if tab == 'onglet-0':
        return [page_daccueil]
    elif tab == 'onglet-1':
        # Gérez l'onglet Cartographie
        return dbc.Row([
            dbc.Col(sidebar, width=3),
            dbc.Col([dcc.Graph(figure=carte)], width=9)
        ])
    elif tab == 'onglet-2':
        # Gérez l'onglet Prédiction prix de vente
        return dbc.Row([
            dbc.Col([prediction_section], width=9, className="mx-auto")
        ])
    elif tab == 'onglet-3':
        # Gérez l'onglet Évolution
        return dbc.Row([
            dbc.Col([
                html.Label("Sélectionnez les Communes"),
                dcc.Dropdown(id='commune-dropdown', options=commune_options, multi=True, value=[]),
                dcc.Graph(id='commune-price-evolution-graph')
            ], width=6),
            dbc.Col([
                html.Label("Sélectionnez les départements"),
                dcc.Dropdown(id='depart-dropdown', options=region_options , multi=True, value=[]),
                dcc.Graph(id='region-price-evolution-graph')  
            ], width=6),
            dbc.Col([
                html.Label("Sélectionnez les Communes"),
                dcc.Dropdown(id='typelocal-dropdown', options=commune_options , multi=True, value=[]),
                dcc.Graph(id='typelocal-price-evolution-diagr')  
            ], width=6)
        ])


if __name__ == '__main__':
    app.run_server(debug=True)

