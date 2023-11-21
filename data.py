import pandas as pd

# Cargar el DataFrame con las noticias similares desde un archivo Excel
df = pd.read_excel("datos/noticiasSimilares.xlsx")

# Mapeo de nombres de periódicos a sus versiones deseadas
nombre_periodicos = {
    'elmundoes': 'EL MUNDO',
    'elpais': 'EL PAÍS',
    'lavanguardia': 'LA VANGUARDIA',
    'elconfidencial': 'EL CONFIDENCIAL',
    'eldiarioes': 'ELDIARIO.ES',
    'larazones': 'LA RAZÓN',
    'marca': 'MARCA'
}

# Definir colores para cada periódico
colores_periodicos = {
    'EL MUNDO': 'mediumslateblue',
    'EL PAÍS': 'darkgray',
    'LA VANGUARDIA': 'darkblue',
    'EL CONFIDENCIAL': 'skyblue',
    'ELDIARIO.ES': 'turquoise',
    'LA RAZÓN': 'darkred',
    'MARCA': 'red'
}

# Asigna la orientación política a una nueva columna en el DataFrame
orientacion_politica = {
    'elconfidencial': 2,  # derecha
    'larazones': 2,  # derecha
    'elmundoes': 1,  # centro-derecha
    'lavanguardia': 0,  # centro
    'marca': 4,  # deportivo
    'elpais': -1,  # centro-izquierda
    'eldiarioes': -2  # izquierda
}

df['Orientación Política'] = df['Periódico'].map(orientacion_politica)

# Filtrar el DataFrame para excluir 'Marca'
df_filtrado = df[df['Periódico'] != 'Marca']

# Ordenar el DataFrame por el número de ocurrencias de cada primer titular similar (descendente)
df_similares = df.groupby(['Titulo Compartido'])
titulo_compartido_set = set()
