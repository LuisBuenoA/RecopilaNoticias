# Importar las bibliotecas necesarias
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import urllib.parse

# Cargar el DataFrame con las noticias similares desde un archivo CSV
df = pd.read_excel("noticiasSimilares.xlsx")

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Ordenar el DataFrame por el número de ocurrencias de cada primer titular similar (descendente)
df_similares = df.groupby(['Titulo Compartido'])

# Define la función para generar el diseño de cada "cuadrado" con un titular similar
def generate_square(titulo_compartido, fecha):
    # Codifica el titular compartido para evitar problemas con caracteres especiales en la URL
    encoded_titulo = urllib.parse.quote(titulo_compartido)
    return html.Div(
        className='six columns',  # Clase CSS para estilos
        children=[
            html.H2(f"Noticia: {titulo_compartido}"),  # Título Compartido
            html.P(f"Fecha: {fecha}"),  # Fecha
            dcc.Link('Ver noticias similares', href=f'/similar/{encoded_titulo}')  # Enlace para ver noticias similares
        ]
    )

def generate_similar_news(primer_titular_comun):
    titulares_similares_div = []
    datos_titulares = df_similares.get_group(primer_titular_comun)
    
    for _, row in datos_titulares.iterrows():
        titulares_similares_div.append(
            html.Div([
                html.H3(f"Titular Similar: {row['Título']}"),  # Titular similar
                html.P(f"Fecha: {row['Fecha']}"),
                html.P(f"Periódico: {row['Periódico']}"),
                html.Hr()  # Línea horizontal para separar noticias
            ])
        )

    return titulares_similares_div

# Define el diseño de la aplicación
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Componente para manejar la URL
    html.Div(id='page-content'),  # Contenido de la página
    html.Div([
        generate_square(titulo_compartido, fecha) for titulo_compartido, fecha in zip(df['Titulo Compartido'], df['Fecha'])
    ]),  # Lista de cuadrados generados a partir de los titulares
])

# Define el callback para actualizar el contenido de la página
@app.callback(Output('page-content', 'children'), [Input('url', 'pathname')])
def display_page(pathname):
    if pathname is None:
        return html.Div()

    if pathname.startswith('/similar/'):
        # Decodifica el titular compartido para obtener el valor original
        primer_titular_comun = urllib.parse.unquote(pathname.split('/')[-1])
        return generate_similar_news(primer_titular_comun)

    return html.Div()

# Inicia la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)

