import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd

# Cargar el DataFrame con las noticias similares
df_similares = pd.read_csv("noticiasSimilares.csv")

# Inicializar la aplicación Dash
app = dash.Dash(__name__)

# Diseño de la aplicación
app.layout = html.Div([
    dcc.Dropdown(
        id='dropdown-titulares',
        options=[{'label': titulo, 'value': i} for i, titulo in enumerate(df_similares['Primer Titular Similar'])],
        value=df_similares['Primer Titular Similar'].iloc[0] 
    ),
    html.Div(id='primer-titular'),
    html.Div(id='noticias-similares')
])

@app.callback(
    Output('primer-titular', 'children'),
    Output('noticias-similares', 'children'),
    Input('dropdown-titulares', 'value')
)
def actualizar_noticias_similares(titular_seleccionado):
    datos_titular = df_similares[df_similares['Primer Titular Similar'] == titular_seleccionado]


    # Obtener el primer titular similar
    primer_titular_similar = html.Div([
        html.H2(f"Primer Titular Similar: {titular_seleccionado}"),
        html.P(f"Fecha: {datos_titular['Fecha'].iloc[0]}"),
        html.P(f"Enlace: {datos_titular['Enlace'].iloc[0]}"),
        html.Hr()
    ])

    # Obtener las noticias similares
    noticias_similares_div = []
    for _, row in datos_titular.iterrows():
        noticias_similares_div.append(
            html.Div([
                html.H3(f"Titular: {row['Título']}"),
                html.P(f"Fecha: {row['Fecha']}"),
                html.P(f"Enlace: {row['Enlace']}"),
                html.Hr()
            ])
        )

    return primer_titular_similar, noticias_similares_div

if __name__ == '__main__':
    app.run_server(debug=True)
