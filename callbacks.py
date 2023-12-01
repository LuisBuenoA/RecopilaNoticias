from datetime import datetime
from dash import html
from dash.dependencies import Input, Output
from generate import generate_square, generate_similar_news
from data import df
import urllib.parse
from layout import create_layout
from utils import parse_date

# Función para registrar los callbacks en una aplicación Dash
def register_callbacks(app):
    # Callback para actualizar el periódico seleccionado
    @app.callback(
        Output('selected-newspaper-store', 'data'),
        [Input('newspaper-selector', 'value')]
    )
    def update_selected_newspaper(value):
        # Devuelve el valor seleccionado en el selector de periódicos
        return value

    # Callback para actualizar el contenido de la página basado en la URL y el periódico seleccionado
    @app.callback(
        Output('page-content', 'children'),
        [Input('url', 'pathname'), Input('selected-newspaper-store', 'data')]
    )
    def update_page_content(pathname, selected_newspaper_data):
        # Procesa la ruta para mostrar noticias similares
        if pathname.startswith('/similar/'):
            common_title = urllib.parse.unquote(pathname.split('/')[-1])

            # Creación del logotipo de la página
            logo = html.Div([html.A(
                html.Img(src='/assets/logo1.png', style={'height': '150px', 'width': 'auto'}),
                href='/')
                ], style={'position': 'relative', 'top': '10px', 'z-index': '1000','textAlign': 'center'}
                )

            # Creación del botón para volver a la página principal
            back_button = html.A(
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

            # Aplicación de filtros basados en el periódico seleccionado
            if selected_newspaper_data in [None, "TODOS LOS PERIÓDICOS"]:
                selected_newspaper_data = None

            # Procesamiento y obtención de fechas válidas para las noticias similares
            grupo_datos = df[df['Titulo Compartido'] == common_title]
            fechas_validas = [(d, grupo_datos[grupo_datos['Fecha'] == d]['Periódico'].iloc[0]) for d in grupo_datos['Fecha'] if d is not None]

            if fechas_validas:
                fecha_mas_antigua, nombre_periodico = min(
                    fechas_validas,
                    key=lambda x: parse_date(x[0], x[1]) or datetime.max)  # Usa datetime.max como valor por defecto

                processed_date = parse_date(fecha_mas_antigua, nombre_periodico)  # Pasa el nombre real del periódico
                formatted_date = processed_date.strftime('%Y/%m-%d %H:%M') if processed_date else 'Fecha desconocida'

            else:
                formatted_date = 'Fecha desconocida'

            # Generación de componentes visuales para mostrar el título y noticias similares
            square = generate_square(common_title, formatted_date)
            similar_news = generate_similar_news(common_title, selected_newspaper_data)
            return  [back_button] + [logo] + [square] + similar_news
