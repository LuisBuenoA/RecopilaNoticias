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

    df_periodicos = df_periodicos.dropna(subset=['Título', 'Cuerpo'])  # Drop rows with NaN values in Título or Cuerpo

    titulares=df_periodicos["Título"]
    cuerpos=df_periodicos["Cuerpo"]
    periodicos = df_periodicos["Periódico"].tolist()

    # Unir titulares y cuerpos para formar un solo texto por noticia
    textos_noticias = [titulo + " " + cuerpo for titulo, cuerpo in zip(titulares, cuerpos)]

    # Tokenización y preprocesamiento del texto
    nltk.download('punkt')
    nltk.download('stopwords')
    stop_words = set(stopwords.words('spanish'))
    ps = PorterStemmer()

    def preprocess(texto):
        tokens = word_tokenize(texto.lower())
        tokens = [ps.stem(t) for t in tokens if t.isalnum() and t not in stop_words]
        return ' '.join(tokens)

    textos_preprocesados = [preprocess(texto) for texto in textos_noticias]

    # Crear una matriz TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(textos_preprocesados)

    # Calcular similitud de coseno
    similarity_matrix = cosine_similarity(tfidf_matrix)
    
    # Definir un umbral de similitud para considerar noticias como similares
    umbral_similitud = 0.5

    # Encontrar noticias similares
    for i in range(len(titulares)):
        noticias_similares_periodico = []
        for j in range(len(titulares)):
            if similarity_matrix[i][j] > umbral_similitud and (periodicos[i] != periodicos[j]):
                noticias_similares_periodico.append((periodicos[j], j))
        noticias_similares.append((periodicos[i], i, noticias_similares_periodico))

    return noticias_similares

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
df_similares = pd.DataFrame(noticias_similares, columns=['Periódico', 'Índice', 'Noticias Similares'])

# Guardar el DataFrame en un archivo CSV
df_similares.to_csv("noticiasSimilares.csv", index=False) 
