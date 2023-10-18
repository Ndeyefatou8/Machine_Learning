import pandas as pd
import seaborn as sns

#path = "C:/Users/pierr/Documents/1_projet_python/Valeur_fonciere/Depot_data/"
url = 'https://github.com/Pioterr/projet_sise_stock/blob/main/concat.zip?raw=true'

#Test sur le csv concat
#D = pd.read_csv(filepath_or_buffer= path + "concat.csv", sep="|", decimal=",")
D = pd.read_csv(filepath_or_buffer= url ,sep='|', compression='zip')

df = D

d_type = {
    'Commune' : 'str',
    'Code commune' : 'str',
    'Code departement' : 'str',
    'Code postal' : 'str',
    'Valeur fonciere' : 'float',
    'Surface reelle bati' : 'float',
    'Nombre pieces principales' : 'float',
    'Surface terrain' : 'float'
}


df = df.astype(d_type)
df['Date mutation'] = pd.to_datetime(df['Date mutation'], format="%d/%m/%Y")
df[['Valeur fonciere','Nombre pieces principales']] = df[['Valeur fonciere','Nombre pieces principales']].astype('int')

#Uniformisation du code departement
df['Code departement'] = df['Code departement'].str.zfill(2)

#Colonne année et mois
df['month'] = df['Date mutation'].dt.month
df['year'] = df['Date mutation'].dt.year
df = df.drop(labels='Date mutation', axis=1)


df_m2 = df[df['Type local'] != 'Dépendance']
df_m2 = df_m2[df_m2['Surface reelle bati']!=0]

df_m2['prix_m2'] = df_m2['Valeur fonciere'] / df_m2['Surface reelle bati']

group = df_m2.groupby(['Code departement', 'year'], as_index=False)
df_test = pd.DataFrame(group['prix_m2'].mean())
df_test = df_test.rename(columns={'prix_m2': 'Prix m2 moyen region'})

prixm2_r = pd.merge(left=df, right=df_test, on=['Code departement','year'], how='left')

