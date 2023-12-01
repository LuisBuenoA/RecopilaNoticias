import re
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

# Carga el modelo de procesamiento de lenguaje natural en español de spaCy
nlp = spacy.load('es_core_news_sm')

# Función para limpieza y normalización de títulos de noticias
def clean_title(title):
    # Eliminación de saltos de línea y espacios extra
    title = title.replace('\n', ' ').replace('\r', ' ').strip()
    # Reducción de múltiples espacios a uno solo
    title = re.sub(r'\s+', ' ', title)
    return title

# Función para determinar si un string es una URL
def is_url(s):
    if pd.isna(s):
        return False
    # Verificación mediante expresión regular para estructuras de URL
    return bool(re.match(
        r'^(https?|ftp)://[^\s/$.?#].[^\s]*$', s, re.IGNORECASE))

# Función principal para encontrar noticias similares en un conjunto de datos
def noticias_similares(df_periodicos):
    # Eliminación de filas con valores NaN en columnas clave
    df_periodicos = df_periodicos.dropna(subset=['Título', 'Cuerpo', 'Fecha'])

    # Inicialización de listas y extracción de datos relevantes
    noticias_similares = []
    titulares = df_periodicos["Título"].fillna('').tolist()
    cuerpos = df_periodicos["Cuerpo"].fillna('').tolist()
    fechas = df_periodicos["Fecha"].fillna('').tolist()
    periodicos = df_periodicos["Periódico"].tolist()
    enlaces = df_periodicos["Enlace"].fillna('').tolist() 

    # Preprocesamiento de textos y cálculo de similitud
    titulares_procesados = preprocess_text(titulares)
    cuerpos_procesados = preprocess_text(cuerpos)
    similarity_matrix_titulares = calculate_similarity(titulares_procesados)
    similarity_matrix_cuerpos = calculate_similarity(cuerpos_procesados)

    # Umbral de similitud para considerar noticias como similares
    umbral_similitud = 0.3

    for i in range(len(titulares)):
        noticias_similares_titulares = []
        primer_titular_similar = None  

        for j in range(len(titulares)):
            # Comparación de similitud entre titulares y cuerpos de noticias
            if similarity_matrix_titulares[i][j] > umbral_similitud or similarity_matrix_cuerpos[i][j] > umbral_similitud:
                
                # Asegurar que las noticias comparadas sean de diferentes periódicos
                if (periodicos[i] != periodicos[j]):
                    noticias_similares_titulares.append((titulares[j], j))

                # Registro del primer titular similar encontrado
                if primer_titular_similar is None:
                    primer_titular_similar = titulares[j]
                
                # Asignar 'None' si no se encuentran titulares similares
                if not noticias_similares_titulares: 
                    primer_titular_similar = None

        noticias_similares.append((periodicos[i], fechas[i], titulares[i], cuerpos[i], noticias_similares_titulares, primer_titular_similar, enlaces[i])) 

    return noticias_similares

# Función de preprocesamiento de texto para análisis de similitud
def preprocess_text(text):
    nltk.download('punkt')
    nltk.download('stopwords')
    stop_words = set(stopwords.words('spanish'))

    def preprocess(texto):
        # Lematización y filtrado de stopwords usando spaCy
        doc = nlp(texto.lower())
        tokens = [token.lemma_ for token in doc if token.is_alpha and token.lemma_ not in stop_words]
        return ' '.join(tokens)

    return [preprocess(t) for t in text]

# Función para calcular la similitud coseno entre textos
def calculate_similarity(textos_preprocesados):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(textos_preprocesados)
    return cosine_similarity(tfidf_matrix)

# Carga y unificación de datasets de diferentes periódicos
df_elmundo = pd.read_excel("datos/elmundoes.xlsx")
df_elpais = pd.read_excel("datos/elpais.xlsx")
df_lavanguardia = pd.read_excel("datos/lavanguardia.xlsx")
df_elconfidencial = pd.read_excel("datos/elconfidencial.xlsx")
df_lavozdegaliciaes = pd.read_excel("datos/lavozdegaliciaes.xlsx")
df_eldiarioes = pd.read_excel("datos/eldiarioes.xlsx")
df_larazones = pd.read_excel("datos/larazones.xlsx")
df_marca = pd.read_excel("datos/marca.xlsx")

df_periodicos = pd.concat([df_elmundo, df_elpais, df_lavanguardia, df_elconfidencial, df_lavozdegaliciaes, df_eldiarioes, df_larazones, df_marca], axis=0)

# Limpieza de títulos de noticias
df_periodicos['Título'] = df_periodicos['Título'].apply(clean_title)

# Ejecución de la función para encontrar noticias similares
noticias_similares = noticias_similares(df_periodicos)

# Creación de DataFrame con los resultados
df_similares = pd.DataFrame(noticias_similares, columns=['Periódico', 'Fecha', 'Título', 'Cuerpo', 'Títulos Similares', 'Titulo Compartido', 'Enlace'])

# Asignación de valor por defecto en caso de no encontrar título compartido
df_similares['Titulo Compartido'] = df_similares['Titulo Compartido'].fillna("Ninguno")

# Exportación de resultados a un archivo Excel
df_similares.to_excel("datos/noticiasSimilares.xlsx", index=False)
