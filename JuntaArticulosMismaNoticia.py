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

        primer_titular_similar = None  

        for j in range(len(titulares)):
            if similarity_matrix_titulares[i][j] > umbral_similitud or similarity_matrix_cuerpos[i][j] > umbral_similitud:
                
                if (periodicos[i] != periodicos[j]):
                    noticias_similares_titulares.append((titulares[j], j))

                if primer_titular_similar is None:
                    primer_titular_similar = titulares[j]

        noticias_similares.append((periodicos[i], fechas[i], titulares[i], cuerpos[i], noticias_similares_titulares, primer_titular_similar, enlaces[i]))  

    # Pasada adicional para actualizar los primeros titulares similares
    for i, (_, _, _, _, tit_similares, primer_titular_similar, _) in enumerate(noticias_similares):
        if tit_similares:
            for item in tit_similares:
                if isinstance(item, tuple):  # Handle tuples
                    tit_similar, j = item
                    if j < len(noticias_similares):
                        peri, _, _, _, _, _, _ = noticias_similares[j]
                        noticias_similares[j] = (peri, _, _, _, _, primer_titular_similar if primer_titular_similar else tit_similar, _)
                elif isinstance(item, str):  # Handle strings (links)
                    print(f"Skipping link: {item}")
                else:
                    print(f"Unexpected item: {item}")

    # Asignar el mismo Título Compartido a todas las noticias similares
    for i, (_, _, _, _, tit_similares, _, _) in enumerate(noticias_similares):
        for item in tit_similares:
            if isinstance(item, tuple):
                _, j = item
                noticias_similares[j] = (*noticias_similares[j][:6], tit_similares, *noticias_similares[j][7:])
            else:
                print(f"Unexpected item: {item}")


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
df_elmundo = pd.read_excel("elmundoes.xlsx")
df_elpais = pd.read_excel("elpais.xlsx")
df_lavanguardia = pd.read_excel("lavanguardia.xlsx")
df_elconfidencial = pd.read_excel("elconfidencial.xlsx")
df_lavozdegaliciaes = pd.read_excel("lavozdegaliciaes.xlsx")
df_eldiarioes = pd.read_excel("eldiarioes.xlsx")
#df_elespanol = pd.read_excel("elespanol.xlsx")
df_larazones = pd.read_excel("larazones.xlsx")
df_marca = pd.read_excel("marca.xlsx")

df_periodicos = pd.concat([df_elmundo, df_elpais, df_lavanguardia, df_elconfidencial, df_lavozdegaliciaes, df_eldiarioes, df_larazones, df_marca], axis=0)

noticias_similares = noticiasSimilares(df_periodicos)

# Crear DataFrame con noticias similares
df_similares = pd.DataFrame(noticias_similares, columns=['Periódico', 'Fecha', 'Título', 'Cuerpo', 'Títulos Similares', 'Titulo Compartido', 'Enlace'])

# Guardar el DataFrame en un archivo Excel
df_similares.to_excel("noticiasSimilares.xlsx", index=False)