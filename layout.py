from datetime import datetime
from dash import html, dcc
from generate import generate_square
from data import df_similares, titulo_compartido_set, df
from utils import parse_date
from generate_graphs import generate_newspaper_graph, generate_scatter_titles

scatter_titles = generate_scatter_titles()
newspaper_graph_component = generate_newspaper_graph()

def create_layout():
    # Preparar los cuadrados para cada titular
    cuadrados = []

            # Logo en la parte superior derecha
    cuadrados.append(html.Div([html.A(
                html.Img(src='/assets/logo1.png', style={'height': '150px', 'width': 'auto'}),
                href='/')
                ], style={'position': 'relative', 'top': '10px', 'z-index': '1000','textAlign': 'center'}
                ))

    cuadrados.append(newspaper_graph_component)

    cuadrados.append(scatter_titles)

    for titulo_compartido, _, _ in sorted(
            [
                (titulo_compartido, fecha, len(df_similares.get_group(titulo_compartido)))
                for titulo_compartido, fecha in zip(df['Titulo Compartido'], df['Fecha'])
            ],
            key=lambda x: x[2],  # Ordena por el número de noticias similares
            reverse=True  # Orden descendente
        ):
        if titulo_compartido != "Ninguno" and titulo_compartido not in titulo_compartido_set and (titulo_compartido_set.add(titulo_compartido) or True):
            # Obtener el grupo de datos para este titular
            grupo_datos = df_similares.get_group(titulo_compartido)
            
            # Filtrar fechas que no son None y obtener los nombres de los periódicos correspondientes
            fechas_validas = [(d, grupo_datos[grupo_datos['Fecha'] == d]['Periódico'].iloc[0]) for d in grupo_datos['Fecha'] if d is not None]

            # Asegurarse de que hay fechas válidas antes de proceder
            if fechas_validas:
                fecha_mas_antigua, nombre_periodico = min(
                    fechas_validas,
                    key=lambda x: parse_date(x[0], x[1]) or datetime.max)  # Usa datetime.max como valor por defecto

                # Procesar la fecha más antigua
                processed_date = parse_date(fecha_mas_antigua, nombre_periodico)  # Pasa el nombre real del periódico
                formatted_date = processed_date.strftime('%Y/%m/%d %H:%M') if processed_date else 'Fecha desconocida'

                # Generar y añadir el cuadrado
                cuadrado = generate_square(titulo_compartido, formatted_date)
                cuadrados.append(cuadrado)

    return html.Div([
        dcc.Location(id='url', refresh=False),  # Componente para manejar la URL
        dcc.Store(id='selected-newspaper-store'),
        html.Div(id='page-content'),  # Contenido de la página
        html.Div(id='all-squares', children=cuadrados)
    ])