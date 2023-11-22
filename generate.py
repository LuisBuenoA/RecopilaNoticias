from dash import dcc, html
import urllib.parse
from utils import parse_date
from generate_graphs import generate_media_spectrum, generate_time_graph
from data import df_similares, nombre_periodicos

# Define la función para generar el diseño de cada "cuadrado" con un titular similar
def generate_square(titulo_compartido, fecha, periodico_seleccionado=None):
    # Codifica el titular compartido para evitar problemas con caracteres especiales en la URL
    encoded_titulo = urllib.parse.quote(titulo_compartido)

    # Define estilos para que los enlaces parezcan encabezados en lugar de enlaces
    link_style = {
        'color': 'black',  # El color del texto, igual al texto normal
        'textDecoration': 'none',  # Elimina el subrayado de los enlaces
        'font-weight': 'bold',  # Hace que la fuente sea en negrita como un encabezado
        'font-size': '24px' # Ajusta el tamaño del texto al de un encabezado
    }

    # Crea una lista de componentes hijos que incluyen el enlace, la fecha y la gráfica
    children = [
        dcc.Link(
            html.H2(titulo_compartido),  # Título Compartido como enlace
            href=f'/similar/{encoded_titulo}',
            style=link_style  # Aplica los estilos definidos al enlace
        ),
        html.P(f"{fecha}"),  # Fecha
        generate_time_graph(titulo_compartido, periodico_seleccionado)  # Gráfica de tiempo
    ]

    return html.Div(
        className='six columns',  # Clase CSS para estilos
        style={'margin': '10px 30px 0px 30px'},  # Añade un margen inferior para separar los cuadrados
        children=children
    )

def generate_similar_news(primer_titular_comun, periodico_seleccionado=None):
    titulares_similares_div = []
    titulares_utilizados = set()

    datos_titulares = df_similares.get_group(primer_titular_comun).copy()

    # Filtrar por periódico seleccionado si hay uno
    if periodico_seleccionado:
        datos_titulares = datos_titulares[datos_titulares['Periódico'] == periodico_seleccionado]

    periodicos_disponibles = datos_titulares['Periódico'].unique()

    if datos_titulares.shape[0] > 0:
        opciones_periodicos = [{'label': nombre_periodicos[periodico], 'value': periodico} for periodico in periodicos_disponibles]
        titulo_selector = html.H4(['Filtra el periódico que quieras'], style={'font-weight': 'bold','margin': '5px 10px 5px 10px'})
        selector_periodico = dcc.Dropdown(
            id='newspaper-selector',
            options = [{'label': 'TODOS LOS PERIÓDICOS', 'value': 'TODOS LOS PERIÓDICOS'}] + opciones_periodicos,
            value = periodico_seleccionado,
            clearable=False,
            style={'margin': '5px 0px 5px 0px'}
        )

    datos_titulares['Periódico Formateado'] = datos_titulares['Periódico'].map(nombre_periodicos) 

    # Crea el espectro político de medios
    spectrum = generate_media_spectrum(datos_titulares, periodico_seleccionado)

    # Añade el espectro al layout de los titulares similares
    titulares_similares_div.append(spectrum)
    titulares_similares_div.insert(1, titulo_selector)
    titulares_similares_div.insert(2, selector_periodico)

    # Define estilos para que los enlaces parezcan encabezados en lugar de enlaces
    link_style = {
        'color': 'black',  # El color del texto, igual al texto normal
        'textDecoration': 'none',  # Elimina el subrayado de los enlaces
        'font-weight': 'bold',  # Hace que la fuente sea en negrita como un encabezado
        'font-size': '20px'  # Ajusta el tamaño del texto al de un encabezado
    }

    for _, row in datos_titulares.iterrows():
        titular_similar = row['Título']
        enlace_articulo = row['Enlace']
        periodico_formateado = row['Periódico Formateado']  # Usa el nombre formateado del periódico

        # Procesar la fecha usando parse_date
        processed_date = parse_date(row['Fecha'], row['Periódico'])
        # Formatear la fecha procesada según sea necesario
        formatted_date = processed_date.strftime('%Y/%m/%d %H:%M')

        if titular_similar not in titulares_utilizados:
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