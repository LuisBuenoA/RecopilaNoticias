import re
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Define la función para limpiar los títulos
def clean_title(title):
    # Elimina los saltos de línea y los retornos de carro
    title = title.replace('\n', ' ').replace('\r', ' ')
    # Reduce múltiples espacios a un solo espacio
    title = re.sub(r'\s+', ' ', title)
    # Elimina los espacios al inicio y al final de la cadena
    return title.strip()

# Define la función para verificar si un string es una URL
def is_url(s):
    if pd.isna(s):  # Si el valor es NaN, no es una URL
        return False
    # Esta expresión regular comprueba si el string contiene una estructura de URL típica
    return bool(re.match(
        r'^(https?|ftp)://[^\s/$.?#].[^\s]*$', s, re.IGNORECASE))

def noticias_similares(df_periodicos):
    # Omitimos las filas con NaN en las columnas relevantes
    df_periodicos = df_periodicos.dropna(subset=['Título', 'Cuerpo', 'Fecha'])

    noticias_similares = []
    titulares = df_periodicos["Título"].fillna('').tolist()
    cuerpos = df_periodicos["Cuerpo"].fillna('').tolist()
    fechas = df_periodicos["Fecha"].fillna('').tolist()
    periodicos = df_periodicos["Periódico"].tolist()
    enlaces = df_periodicos["Enlace"].fillna('').tolist() 

    titulares_procesados = preprocess_text(titulares)
    cuerpos_procesados = preprocess_text(cuerpos)

    similarity_matrix_titulares = calculate_similarity(titulares_procesados)
    similarity_matrix_cuerpos = calculate_similarity(cuerpos_procesados)

    umbral_similitud = 0.3

    for i in range(len(titulares)):
        noticias_similares_titulares = []

        primer_titular_similar = None  

        for j in range(len(titulares)):
            if similarity_matrix_titulares[i][j] > umbral_similitud or similarity_matrix_cuerpos[i][j] > umbral_similitud:
                
                if (periodicos[i] != periodicos[j]):
                    noticias_similares_titulares.append((titulares[j], j))

                if primer_titular_similar is None:
                    primer_titular_similar = titulares[j]
                # Establecer 'Título Compartido' en None si 'Títulos Similares' está vacío
                if not noticias_similares_titulares: 
                    primer_titular_similar = None

        noticias_similares.append((periodicos[i], fechas[i], titulares[i], cuerpos[i], noticias_similares_titulares, primer_titular_similar, enlaces[i])) 

    return noticias_similares


def preprocess_text(text):
    nltk.download('punkt')
    nltk.download('stopwords')
    stop_words = set(stopwords.words('spanish'))

    # Procesamos los textos sin aplicar stemming para mantener la forma completa de las palabras
    def preprocess(texto):
        tokens = word_tokenize(texto.lower())
        tokens = [t for t in tokens if t.isalnum() and t not in stop_words]
        return ' '.join(tokens)

    return [preprocess(t) for t in text]

def calculate_similarity(textos_preprocesados):
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(textos_preprocesados)
    return cosine_similarity(tfidf_matrix)


# Importamos los datos
df_elmundo = pd.read_excel("datos/elmundoes.xlsx")
df_elpais = pd.read_excel("datos/elpais.xlsx")
df_lavanguardia = pd.read_excel("datos/lavanguardia.xlsx")
df_elconfidencial = pd.read_excel("datos/elconfidencial.xlsx")
df_lavozdegaliciaes = pd.read_excel("datos/lavozdegaliciaes.xlsx")
df_eldiarioes = pd.read_excel("datos/eldiarioes.xlsx")
#df_elespanol = pd.read_excel("datos/elespanol.xlsx")
df_larazones = pd.read_excel("datos/larazones.xlsx")
df_marca = pd.read_excel("datos/marca.xlsx")

df_periodicos = pd.concat([df_elmundo, df_elpais, df_lavanguardia, df_elconfidencial, df_lavozdegaliciaes, df_eldiarioes, df_larazones, df_marca], axis=0)

# Aplica la función a la columna 'Título'
df_periodicos['Título'] = df_periodicos['Título'].apply(clean_title)

noticias_similares = noticias_similares(df_periodicos)

# Crear DataFrame con noticias similares
df_similares = pd.DataFrame(noticias_similares, columns=['Periódico', 'Fecha', 'Título', 'Cuerpo', 'Títulos Similares', 'Titulo Compartido', 'Enlace'])

df_similares['Titulo Compartido'] = df_similares['Titulo Compartido'].fillna("Ninguno")
# Guardar el DataFrame en un archivo Excel
df_similares.to_excel("noticiasSimilares.xlsx", index=False)