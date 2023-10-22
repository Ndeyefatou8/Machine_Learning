# Creation de la fonction de traitement de donnée

### Lib
import pandas as pd


### Set up
path = "C:/Users/pierr/Documents/1_projet_python/Valeur_fonciere/Depot_data/"
#path = "C:/Users/pterron/Documents/projet_python/Application_ml/Depot_data/"

l_fichier = [path+"valeursfoncieres-2018.txt",path+"valeursfoncieres-2019.txt",path+"valeursfoncieres-2020.txt",path+"valeursfoncieres-2021.txt"]


## Methode

def charge_ass_df(list_p, sep="|", decimal=","):
    #list_p dois etre une liste de taille 2 minimum
    #Check len
    if(len(list_p) <2 ):
        print("len(Arg) < 2")
        return
    
    df_fin = pd.read_csv(filepath_or_buffer= list_p[0], sep=sep, decimal=decimal)
    
    #Charge et assemble
    for i in range(1 ,len(list_p)):

        df_temp = pd.read_csv(filepath_or_buffer= list_p[i], sep=sep, decimal=decimal)
        df_fin = pd.concat([df_fin , df_temp])
    
    return df_fin


def traiter_df(dataframe,l_man = []):
    #Supprimer les colonnes et lignes en trop
    #Colonne vide
    dataframe = dataframe.dropna(axis = 1, how='all')
    #Colonne Pourcentage de valeur vide
    perc = len(dataframe)*0.30 # >70%
    dataframe = dataframe.dropna(axis = 1, thresh = perc)
    
    #Lignes
    dataframe = dataframe.dropna(axis =0, subset='Valeur fonciere') #Valeur cible nulle
    dataframe = dataframe.dropna(axis = 0, subset='Type local') #Type local null
    dataframe = dataframe.dropna(axis = 0, subset='Code postal') #Code postal null
    dataframe = dataframe.dropna(axis = 0, subset='Code postal') # drop les non vente
    dataframe = dataframe[dataframe['Nature mutation'] == 'Vente']
    
    
    #Supprimer les doublons pour supprimer les dependances
    dataframe['discretisation'] = dataframe['Date mutation'].astype(str) + dataframe['Code voie'].astype(str) + dataframe['Voie'].astype(str) + dataframe['Commune'].astype(str)
    dataframe = dataframe.drop_duplicates(subset = 'discretisation', keep=False)
    dataframe = dataframe.drop(labels='discretisation', axis = 1) #Suppr colonne
    #Suppression arbitraire des colonnes restantes (l_man)
    dataframe = dataframe.drop(labels=l_man, axis = 1) #Suppr colonne l_man

    return dataframe


def fill_na_val(dataframe):
    #Type de voie (mode, Rue à 50% dans la distribution / 10% de remplissage de valuer manquante)
    dataframe['Type de voie'] = dataframe['Type de voie'].fillna(value = df['Type de voie'].mode()[0])
    dataframe['Nature culture'] = dataframe['Nature culture'].map(lambda x: 1 if x =='S' else 0) # Binarisation, 1 si S sinon
    dataframe['Type de voie'] = dataframe['Type de voie'].fillna(value = dataframe['Type de voie'].mode()[0])
    dataframe['Surface reelle bati'] = dataframe['Surface reelle bati'].fillna(value = dataframe['Surface reelle bati'].median())
    dataframe['Nombre pieces principales'] = dataframe['Nombre pieces principales'].fillna(value = 4) # mode
    dataframe['Surface terrain'].loc[dataframe['Surface terrain'].isna() & (dataframe['Type local'] == 'Appartement')] = 0 #Remplacement des surface terrain par 0 pour le sappartements, et on vire les autres lignes valeurs vide
    dataframe = dataframe.dropna(axis = 0, subset='Surface terrain') # On supprime les lignes sans valeur

    return dataframe

def remove_outlier_quartile(df):
    #drop valeur fonciere outlier
    Q1 = df['Valeur fonciere'].quantile(0.25)
    Q3 = df['Valeur fonciere'].quantile(0.75)
    IQR = Q3 - Q1

    df = df[(df['Valeur fonciere'] >= Q1 - 1.5 * IQR) & (df['Valeur fonciere'] <= Q3 + 1.5 * IQR)]

    #drop Surface réelle outlier
    Q1 = df['Surface reelle bati'].quantile(0.25)
    Q3 = df['Surface reelle bati'].quantile(0.75)
    IQR = Q3 - Q1

    df = df[(df['Surface reelle bati'] >= Q1 - 1.5 * IQR) & (df['Surface reelle bati'] <= Q3 + 1.5 * IQR)]

    #drop Nombre pièce principales
    Q1 = df['Nombre pieces principales'].quantile(0.25)
    Q3 = df['Nombre pieces principales'].quantile(0.75)
    IQR = Q3 - Q1

    df = df[(df['Nombre pieces principales'] >= Q1 - 1.5 * IQR) & (df['Nombre pieces principales'] <= Q3 + 1.5 * IQR)]

    #drop Surface terrain
    Q1 = df['Surface terrain'].quantile(0.25)
    Q3 = df['Surface terrain'].quantile(0.75)
    IQR = Q3 - Q1

    df = df[(df['Surface terrain'] >= Q1 - 1.5 * IQR) & (df['Surface terrain'] <= Q3 + 1.5 * IQR)]

    return df

def prix_m2_region_annee(df):
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

    #On calcul ce prix hors dépendances
    df_m2 = df[df['Type local'] != 'Dépendance']
    df_m2 = df_m2[df_m2['Surface reelle bati']!=0]

    #Calcul du prix au m²
    df_m2['prix_m2'] = df_m2['Valeur fonciere'] / df_m2['Surface reelle bati']
    
    #Prix departement
    dep = df_m2.groupby(['Code departement', 'year'], as_index=False)
    df_dep = pd.DataFrame(dep['prix_m2'].mean())
    df_dep = df_dep.rename(columns={'prix_m2': 'Prix m2 moyen region'})

    # Prix commune
    com = df_m2.groupby(['Commune','Code departement', 'year'], as_index=False)
    df_com = pd.DataFrame(com['prix_m2'].mean())
    df_com = df_com.rename(columns={'prix_m2': 'Prix m2 moyen commune'})

    #Fusion des dataset
    prixm2_r = pd.merge(left=df, right=df_dep, on=['Code departement','year'], how='left')
    prixm2_rc = pd.merge(left=prixm2_r, right=df_com, on=['Commune','Code departement', 'year'], how='left')

    prixm2_rc['Prix m2 moyen commune'].fillna(prixm2_rc['Prix m2 moyen region'], inplace= True)

    return prixm2_rc


def latitude_longi(df):
    # Ajout des latitude longitude
    d_type = {
    'Commune' : 'str',
    'Code commune' : 'float',
    'Code departement' : 'str',
    'Code postal' : 'str',
    'Valeur fonciere' : 'float',
    'Surface reelle bati' : 'float',
    'Nombre pieces principales' : 'float',
    'Surface terrain' : 'float'
    }


    df = df.astype(d_type)
    df['Code commune'] = df['Code commune'].astype(int).astype(str)

    #Import des données
    lat = pd.read_csv(filepath_or_buffer= "C:/Users/pierr/Documents/1_projet_python/Valeur_fonciere/Depot_data/communes-departement-region.csv", sep=",", decimal=".")

    lat = lat[['code_commune_INSEE','nom_commune_postal','code_postal','latitude', 'longitude','code_commune','code_departement']]
    lat = lat.dropna(axis=0)

    #Transtypage
    d_type = {
        'code_commune_INSEE':'str',
        'nom_commune_postal':'str',
        'code_postal':'float',
        'latitude':'float',
        'longitude':'float',
        'code_commune':'float',
        'code_departement':'str'
    }


    lat = lat.astype(d_type)
    lat['code_commune'] = lat['code_commune'].astype(int).astype(str)
    lat['code_postal'] = lat['code_postal'].astype(str)

    #Renommage des colonnes
    lat_fu = lat[['code_departement','code_commune','code_postal', 'latitude', 'longitude']]
    lat_fu = lat_fu.rename(columns={'code_departement': 'Code departement', 'code_commune': 'Code commune', 'code_postal' : 'Code postal'})

    lat_fu.drop_duplicates(inplace = True)

    #Union des deux tables
    result = pd.merge(left=df, right=lat_fu, on=['Code departement','Code commune', 'Code postal'], how='left')

    #On remplace les valeurs nulles par zero
    values = {"latitude": 0, "longitude":0}
    #result.fillna(value = values, inplace= True)
    
    return result

#### Appel de la methode

# Ecrire en csv (2 G0)
#charge_ass_df(l_fichier).to_csv(path_or_buf= path + "concat.csv", sep = "|", )
var_drop = ['No disposition', 'No voie', 'Code voie', 'Voie', 'Section','No plan','1er lot']
df = charge_ass_df(l_fichier)

df = traiter_df(df, var_drop)

df = fill_na_val(df)
df = remove_outlier_quartile(df)
df = prix_m2_region_annee(df)
df = latitude_longi(df)

print(df.shape)
#print(df.isnull().sum()/len(df) *100)
df.to_csv(path_or_buf= path + "concat_prix_m2_lati_test.csv", sep = "|", index= False)


print('fini')