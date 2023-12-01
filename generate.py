from dash import dcc, html
import urllib.parse
from utils import parse_date
from generate_graphs import generate_media_spectrum, generate_time_graph
from data import df_similares, nombre_periodicos

# Función para generar el diseño de cada "cuadrado" con un titular similar
def generate_square(titulo_compartido, fecha, periodico_seleccionado=None):
    # Codificación del titular compartido para su uso en URL
    encoded_titulo = urllib.parse.quote(titulo_compartido)

    # Estilos para los enlaces, haciéndolos parecer encabezados
    link_style = {
        'color': 'black',
        'textDecoration': 'none',
        'font-weight': 'bold',
        'font-size': '24px'
    }

    # Creación de componentes HTML para el cuadrado, incluyendo enlace y fecha
    children = [
        dcc.Link(
            html.H2(titulo_compartido),
            href=f'/similar/{encoded_titulo}',
            style=link_style
        ),
        html.P(f"{fecha}"),
        generate_time_graph(titulo_compartido, periodico_seleccionado)
    ]

    return html.Div(
        className='six columns',
        style={'margin': '10px 30px 0px 30px'},
        children=children
    )

# Función para generar noticias similares en la página
def generate_similar_news(primer_titular_comun, periodico_seleccionado=None):
    titulares_similares_div = []
    titulares_utilizados = set()

    # Filtrado de datos basado en el titular común
    datos_titulares = df_similares.get_group(primer_titular_comun).copy()

    # Filtro opcional por periódico
    if periodico_seleccionado:
        datos_titulares = datos_titulares[datos_titulares['Periódico'] == periodico_seleccionado]

    # Creación del espectro de medios y selector de periódico
    periodicos_disponibles = datos_titulares['Periódico'].unique()

    if datos_titulares.shape[0] > 0:
        opciones_periodicos = [{'label': nombre_periodicos[periodico], 'value': periodico} for periodico in periodicos_disponibles]
        titulo_selector = html.H4(['Filtra por periódico'], style={'font-weight': 'bold', 'textAlign': 'center', 'margin': '20px 0 20px 0'})
        selector_periodico = dcc.Dropdown(
            id='newspaper-selector',
            options = [{'label': 'TODOS LOS PERIÓDICOS', 'value': 'TODOS LOS PERIÓDICOS'}] + opciones_periodicos,
            value = periodico_seleccionado,
            clearable=False,
            style={'margin': '5px 0px 20px 0px'}
        )

    datos_titulares['Periódico Formateado'] = datos_titulares['Periódico'].map(nombre_periodicos) 

    # Crea el espectro político de medios
    spectrum = generate_media_spectrum(datos_titulares, periodico_seleccionado)

    # Añade el espectro al layout de los titulares similares
    titulares_similares_div.append(spectrum)
    titulares_similares_div.insert(1, titulo_selector)
    titulares_similares_div.insert(2, selector_periodico)

    # Estilos para enlaces de titulares similares
    link_style = {
        'color': 'black',
        'textDecoration': 'none',
        'font-weight': 'bold',
        'font-size': '20px'
    }

    # Bucle para añadir cada titular similar al layout
    for _, row in datos_titulares.iterrows():
        # Extracción y formateo de datos de cada titular similar
        titular_similar = row['Título']
        enlace_articulo = row['Enlace']
        periodico_formateado = row['Periódico Formateado']  # Usa el nombre formateado del periódico

        # Procesar la fecha usando parse_date
        processed_date = parse_date(row['Fecha'], row['Periódico'])
        # Formatear la fecha procesada según sea necesario
        formatted_date = processed_date.strftime('%Y/%m/%d %H:%M')
        
        # Comprobación para evitar duplicados
        if titular_similar not in titulares_utilizados:
            # Creación de componente para cada titular similar
            titulares_similares_div.append(
                html.Div([
                    dcc.Link(
                        html.H3(titular_similar),  # Titular similar como enlace
                        href=enlace_articulo,
                        target="_blank",  # Abre el enlace en una nueva pestaña
                        style=link_style  # Aplica los estilos definidos al enlace
                    ),
                    html.P(f"{formatted_date}"),
                    html.P(f"{periodico_formateado}"),  # Muestra el nombre formateado
                    html.Hr()  # Línea horizontal para separar noticias
                ],
                style={'margin': '10px 30px 10px 30px'}
                )
            )
            titulares_utilizados.add(titular_similar)
    return titulares_similares_div