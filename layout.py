from datetime import datetime
from dash import html, dcc
from generate import generate_square
from data import df_similares, titulo_compartido_set, df
from utils import parse_date
from generate_graphs import generate_newspaper_graph, generate_scatter_titles

# Generación de gráficos para la visualización de datos
scatter_titles = generate_scatter_titles()
newspaper_graph_component = generate_newspaper_graph()

# Función para crear el layout principal de la aplicación Dash
def create_layout():
    # Inicialización de la lista para almacenar componentes visuales
    cuadrados = []

    # Inserción del logo en la parte superior de la página
    cuadrados.append(html.Div([html.A(
                html.Img(src='/assets/logo1.png', style={'height': '150px', 'width': 'auto'}),
                href='/')
                ], style={'position': 'relative', 'top': '10px', 'z-index': '1000','textAlign': 'center'}
                ))

    # Añadir componentes gráficos al layout
    cuadrados.append(newspaper_graph_component)
    cuadrados.append(scatter_titles)

    # Procesamiento y visualización de titulares compartidos
    for titulo_compartido, _, _ in sorted(
            [
                (titulo_compartido, fecha, len(df_similares.get_group(titulo_compartido)))
                for titulo_compartido, fecha in zip(df['Titulo Compartido'], df['Fecha'])
            ],
            key=lambda x: x[2],  # Ordenamiento basado en el número de noticias similares
            reverse=True  # Orden descendente para mostrar primero los más relevantes
        ):
        # Filtrado y generación de cuadrados para titulares no repetidos
        if titulo_compartido != "Ninguno" and titulo_compartido not in titulo_compartido_set and (titulo_compartido_set.add(titulo_compartido) or True):
            # Extracción de datos para el titular específico
            grupo_datos = df_similares.get_group(titulo_compartido)
            
            # Filtrado de fechas válidas y obtención de nombres de periódicos asociados
            fechas_validas = [(d, grupo_datos[grupo_datos['Fecha'] == d]['Periódico'].iloc[0]) for d in grupo_datos['Fecha'] if d is not None]

            # Procesamiento de la fecha más antigua para obtener la primera mención
            if fechas_validas:
                fecha_mas_antigua, nombre_periodico = min(
                    fechas_validas,
                    key=lambda x: parse_date(x[0], x[1]) or datetime.max)

                # Formateo de la fecha procesada
                processed_date = parse_date(fecha_mas_antigua, nombre_periodico)
                formatted_date = processed_date.strftime('%Y/%m/%d %H:%M') if processed_date else 'Fecha desconocida'

                # Generación del cuadrado con la información del titular y su adición al layout
                cuadrado = generate_square(titulo_compartido, formatted_date)
                cuadrados.append(cuadrado)

    # Creación del layout final con todos los componentes
    return html.Div([
        dcc.Location(id='url', refresh=False),  # Componente para la navegación por URL
        dcc.Store(id='selected-newspaper-store'),  # Almacenamiento de datos de selección de periódico
        html.Div(id='page-content'),  # División para contenido actualizado dinámicamente
        html.Div(id='all-squares', children=cuadrados)  # División que contiene todos los cuadrados generados
    ])