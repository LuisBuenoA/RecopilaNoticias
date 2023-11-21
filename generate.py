from dash import dcc, html
import urllib.parse
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
        'font-size': '24px'  # Ajusta el tamaño del texto al de un encabezado
    }

    # Crea una lista de componentes hijos que incluyen el enlace, la fecha y la gráfica
    children = [
        dcc.Link(
            html.H2(titulo_compartido),  # Título Compartido como enlace
            href=f'/similar/{encoded_titulo}',
            style=link_style  # Aplica los estilos definidos al enlace
        ),
        html.P(f"Fecha: {fecha}"),  # Fecha
        generate_time_graph(titulo_compartido, periodico_seleccionado)  # Gráfica de tiempo
    ]

    return html.Div(
        className='six columns',  # Clase CSS para estilos
        style={'margin-bottom': '10px'},  # Añade un margen inferior para separar los cuadrados
        children=children
    )

def generate_similar_news(primer_titular_comun, periodico_seleccionado=None):
    titulares_similares_div = []
    titulares_utilizados = set()  # Conjunto para realizar un seguimiento de los titulares ya utilizados

    datos_titulares = df_similares.get_group(primer_titular_comun)

    # Filtrar periódicos disponibles para este titular similar
    periodicos_disponibles = datos_titulares['Periódico'].unique()

    # Solo crea el selector de periódicos si hay titulares similares
    if datos_titulares.shape[0] > 0:
        opciones_periodicos = [{'label': nombre_periodicos[periodico], 'value': periodico} for periodico in periodicos_disponibles]
        selector_periodico = dcc.Dropdown(
            id='newspaper-selector',
            options=opciones_periodicos,
            value=periodico_seleccionado,
            clearable=False
        )
        titulares_similares_div.insert(0, selector_periodico)  # Añade al inicio de la lista


    # Aplica el mapeo de nombre_periodicos a la columna 'Periódico'
    datos_titulares['Periódico Formateado'] = datos_titulares['Periódico'].map(nombre_periodicos)

    # Crea el espectro político de medios
    spectrum = generate_media_spectrum(datos_titulares, periodico_seleccionado)

    # Añade el espectro al layout de los titulares similares
    titulares_similares_div.append(spectrum)

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
        if titular_similar not in titulares_utilizados:
            titulares_similares_div.append(
                html.Div([
                    dcc.Link(
                        html.H3(titular_similar),  # Titular similar como enlace
                        href=enlace_articulo,
                        target="_blank",  # Abre el enlace en una nueva pestaña
                        style=link_style  # Aplica los estilos definidos al enlace
                    ),
                    html.P(f"Fecha: {row['Fecha']}"),
                    html.P(f"Periódico: {periodico_formateado}"),  # Muestra el nombre formateado
                    html.Hr()  # Línea horizontal para separar noticias
                ])
            )
            titulares_utilizados.add(titular_similar)
    return titulares_similares_div