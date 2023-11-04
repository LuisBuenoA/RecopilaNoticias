import pandas as pd
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
    enlaces = df_periodicos["Enlace"].fillna('').tolist() 

    titulares_procesados = preprocess_text(titulares)
    cuerpos_procesados = preprocess_text(cuerpos)

    similarity_matrix_titulares = calculate_similarity(titulares_procesados)
    similarity_matrix_cuerpos = calculate_similarity(cuerpos_procesados)

    umbral_similitud = 0.5

    for i in range(len(titulares)):
        noticias_similares_titulares = []
        noticias_similares_cuerpos = []

        primer_titular_similar = None  

        for j in range(len(titulares)):
            if similarity_matrix_titulares[i][j] > umbral_similitud:
                
                if (periodicos[i] != periodicos[j]):
                    noticias_similares_titulares.append((periodicos[j], j))

                if primer_titular_similar is None:
                    primer_titular_similar = titulares[j]

            if similarity_matrix_cuerpos[i][j] > umbral_similitud and (periodicos[i] != periodicos[j]):
                noticias_similares_cuerpos.append((periodicos[j], j))

        noticias_similares.append((periodicos[i], i, fechas[i], titulares[i], cuerpos[i], noticias_similares_titulares, noticias_similares_cuerpos, primer_titular_similar, enlaces[i]))  

    # Pasada adicional para actualizar los primeros titulares similares
    for i, (_, _, _, _, _, tit_similares, _, _, primer_titular_similar) in enumerate(noticias_similares):
        for _, j in tit_similares:
            if j < len(noticias_similares):
                peri, idx, _, _, _, _, _, _, titulares_j = noticias_similares[j]
                noticias_similares[j] = (peri, idx, _, _, _, _, _, _, primer_titular_similar if primer_titular_similar else titulares_j)
    return noticias_similares

def preprocess_text(texto):
    nltk.download('punkt')
    nltk.download('stopwords')
    stop_words = set(stopwords.words('spanish'))
    ps = PorterStemmer()

    def preprocess(texto):
        tokens = word_tokenize(texto.lower())
        tokens = [ps.stem(t) for t in tokens if t.isalnum() and t not in stop_words]
        return ' '.join(tokens)

    if isinstance(texto, list):
        return [preprocess(t) for t in texto]
    else:
        return preprocess(texto)

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

print(noticias_similares)
# Crear DataFrame con noticias similares
df_similares = pd.DataFrame(noticias_similares, columns=['Periódico', 'Índice', 'Fecha', 'Título', 'Cuerpo', 'Títulos Similares', 'Cuerpos Similares', 'Enlace', 'Primer Titular Similar'])

# Guardar el DataFrame en un archivo CSV
df_similares.to_csv("noticiasSimilares.csv", index=False)
