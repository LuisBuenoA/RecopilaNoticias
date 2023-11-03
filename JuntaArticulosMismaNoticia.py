import datetime
import numpy as np
import pandas as pd
from datetime import date, timedelta, datetime
import sklearn.datasets 
import matplotlib.pyplot as plt
import seaborn as sns
import os
import missingno as msno

from sklearn.model_selection import train_test_split
from sklearn.svm import LinearSVC
from sklearn.metrics import (adjusted_mutual_info_score, homogeneity_score,
                            completeness_score,classification_report, confusion_matrix,
                            mean_squared_error, mean_absolute_error,
                            mean_absolute_percentage_error,
                            silhouette_score, v_measure_score, adjusted_rand_score)
from sklearn.linear_model import ElasticNet, SGDClassifier, LogisticRegression
from sklearn.cluster import KMeans, DBSCAN, AffinityPropagation
from sklearn import datasets
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

from matplotlib import colors

import plotly.graph_objects as go
import plotly.express as px
import statsmodels.api as sm

from imblearn.over_sampling import RandomOverSampler
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

def noticiasSimilares(df_periodicos):
    noticias_similares = []
    df_periodicos = df_periodicos.dropna(subset=['Título', 'Cuerpo', 'Fecha'])

    titulares = df_periodicos["Título"].fillna('').tolist()
    cuerpos = df_periodicos["Cuerpo"].fillna('').tolist()
    fechas = df_periodicos["Fecha"].fillna('').tolist()
    periodicos = df_periodicos["Periódico"].tolist()

    titulares_procesados = preprocess_text(titulares)
    cuerpos_procesados = preprocess_text(cuerpos)

    similarity_matrix_titulares = calculate_similarity(titulares_procesados)
    similarity_matrix_cuerpos = calculate_similarity(cuerpos_procesados)

    umbral_similitud = 0.5

    for i in range(len(titulares)):
        noticias_similares_titulares = []
        noticias_similares_cuerpos = []

        for j in range(len(titulares)):
            if similarity_matrix_titulares[i][j] > umbral_similitud and (periodicos[i] != periodicos[j]):
                noticias_similares_titulares.append((periodicos[j], j))

            if similarity_matrix_cuerpos[i][j] > umbral_similitud and (periodicos[i] != periodicos[j]):
                noticias_similares_cuerpos.append((periodicos[j], j))

        noticias_similares.append((periodicos[i], i, fechas[i], titulares[i], cuerpos[i], noticias_similares_titulares, noticias_similares_cuerpos))

    return noticias_similares

def preprocess_text(text):
    nltk.download('punkt')
    nltk.download('stopwords')
    stop_words = set(stopwords.words('spanish'))
    ps = PorterStemmer()

    def preprocess(texto):
        tokens = word_tokenize(texto.lower())
        tokens = [ps.stem(t) for t in tokens if t.isalnum() and t not in stop_words]
        return ' '.join(tokens)

    return [preprocess(t) for t in text]

def calculate_similarity(textos_preprocesados):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(textos_preprocesados)
    return cosine_similarity(tfidf_matrix)


# Importamos los datos
df_elmundo = pd.read_csv("elmundoes.csv")
df_elpais = pd.read_csv("elpais.csv")
df_lavanguardia = pd.read_csv("lavanguardia.csv")
df_elconfidencial = pd.read_csv("elconfidencial.csv")
df_lavozdegaliciaes = pd.read_csv("lavozdegaliciaes.csv")
df_eldiarioes = pd.read_csv("eldiarioes.csv")
#df_elespanol = pd.read_csv("elespanol.csv")
df_larazones = pd.read_csv("larazones.csv")
df_marca = pd.read_csv("marca.csv")

df_periodicos = pd.concat([df_elmundo, df_elpais, df_lavanguardia, df_elconfidencial, df_lavozdegaliciaes, df_eldiarioes, df_larazones, df_marca], axis=0)

noticias_similares = noticiasSimilares(df_periodicos)

# Crear DataFrame con noticias similares
df_similares = pd.DataFrame(noticias_similares, columns=['Periódico', 'Índice', 'Fecha', 'Título', 'Cuerpo', 'Títulos Similares', 'Cuerpos Similares'])

# Guardar el DataFrame en un archivo CSV
df_similares.to_csv("noticiasSimilares.csv", index=False)
