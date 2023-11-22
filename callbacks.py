from datetime import datetime
from dash import html
from dash.dependencies import Input, Output
from generate import generate_square, generate_similar_news
from data import df
import urllib.parse
from layout import create_layout
from utils import parse_date

def register_callbacks(app):
    @app.callback(
        Output('selected-newspaper-store', 'data'),
        [Input('newspaper-selector', 'value')]
    )
    def update_selected_newspaper(value):
        return value
    
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname'), Input('selected-newspaper-store', 'data')]
    )
    def update_page_content(pathname, selected_newspaper_data):
        if pathname.startswith('/similar/'):
            common_title = urllib.parse.unquote(pathname.split('/')[-1])

            # Botón o enlace para volver a la página principal
            back_button = back_button = html.A(
                html.Button(
                    "Atrás",  # Texto del botón
                    id='back-button',  # Identificador único para el botón
                    style={
                        'position': 'relative', 'top': '10px', 'left': '10px',  # Estilos para posicionar el botón
                        'textDecoration': 'none',
                        'fontSize': '16px',  # Tamaño de la fuente
                        'fontWeight': 'bold',  # Peso de la fuente
                        'padding': '10px 20px',  # Relleno alrededor del texto
                        'backgroundColor': '#222222',  # Color de fondo del botón
                        'color': 'white',  # Color del texto
                        'border': 'none',  # Sin borde
                        'borderRadius': '5px',  # Bordes redondeados
                        'cursor': 'pointer',  # Cursor en forma de mano al pasar por encima
                        'boxShadow': '0px 2px 2px lightgrey',  # Sombra del botón
                        'margin-bottom': '10px'
                    }
                ),
                href='/'  # Enlace a la página principal
            )

            # Si selected_newspaper_data es "TODOS LOS PERIÓDICOS" o None, no aplicar ningún filtro
            if selected_newspaper_data in [None, "TODOS LOS PERIÓDICOS"]:
                selected_newspaper_data = None

            # Obtener todas las fechas para este titular y el periódico correspondiente
            grupo_datos = df[df['Titulo Compartido'] == common_title]
            fechas_validas = [(d, grupo_datos[grupo_datos['Fecha'] == d]['Periódico'].iloc[0]) for d in grupo_datos['Fecha'] if d is not None]

            # Encontrar la fecha más antigua y procesarla
            if fechas_validas:
                fecha_mas_antigua, nombre_periodico = min(
                    fechas_validas,
                    key=lambda x: parse_date(x[0], x[1]) or datetime.max)  # Usa datetime.max como valor por defecto

                processed_date = parse_date(fecha_mas_antigua, nombre_periodico)  # Pasa el nombre real del periódico
                formatted_date = processed_date.strftime('%Y/%m-%d %H:%M') if processed_date else 'Fecha desconocida'

            else:
                formatted_date = 'Fecha desconocida'

            square = generate_square(common_title, formatted_date)
            similar_news = generate_similar_news(common_title, selected_newspaper_data)
            return [back_button] + [square] + similar_news
