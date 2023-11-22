from datetime import datetime
import re
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import urllib.parse
import plotly.graph_objs as go
import plotly.express as px

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

# Contar noticias y preparar datos para el gráfico
conteo_noticias = df_filtrado['Orientación Política'].value_counts().sort_index()
bar_data = go.Bar(
    x=conteo_noticias.index, 
    y=conteo_noticias.values, 
    marker=dict(color=conteo_noticias.values, colorscale='Viridis')
)

# Inicializar la aplicación Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Ordenar el DataFrame por el número de ocurrencias de cada primer titular similar (descendente)
df_similares = df.groupby(['Titulo Compartido'])
titulo_compartido_set = set()

# Diccionario de meses en español
months = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
    'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

meses = {
    'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
}

# Función para procesar y convertir las fechas
def parse_date(date_str, periodico):
    try:
        # Dividir la cadena si contiene dos fechas
        if '  ' in date_str:
            date_str = date_str.split('  ')[0]       
        if periodico == 'elmundoes':
            # Formato: "Miércoles,15noviembre2023-12:38"
            match = re.search(r'(\d+)([a-z]+)(\d{4})-(\d{2}):(\d{2})', date_str)
            if match:
                day, month_str, year, hour, minute = match.groups()
                month = months[month_str]
                return datetime(int(year), month, int(day), int(hour), int(minute))
        
        elif periodico == 'elpais':
            # Formato: "15 nov 2023 - 12:34 CET"
            match = re.search(r'(\d{2})\s([a-z]+)\s(\d{4})\s-\s(\d{2}):(\d{2})', date_str)
            if match:
                day, month_str, year, hour, minute = match.groups()
                month = meses[month_str[:3]]
                return datetime(int(year), month, int(day), int(hour), int(minute))

        elif periodico == 'lavanguardia':
            # Formato: "15/11/2023 11:57"
            return datetime.strptime(date_str, '%d/%m/%Y %H:%M')

        elif periodico == 'elconfidencial':
            # Formato: "15/11/2023 - 11:44"
            return datetime.strptime(date_str, '%d/%m/%Y - %H:%M')

        elif periodico == 'eldiarioes':
            # Formato: "14 de noviembre de 202323:22h"
            match = re.search(r'(\d+)\sde\s([a-z]+)\sde\s(\d{4})\s*(\d{2}):(\d{2})h', date_str)
            if match:
                day, month_str, year, hour, minute = match.groups()
                month = months[month_str]
                return datetime(int(year), month, int(day), int(hour), int(minute))

        elif periodico == 'larazones':
            # Formato: "07.11.2023 00:45"
            return datetime.strptime(date_str, '%d.%m.%Y %H:%M')

        elif periodico == 'marca':
            # Formato: "15 de noviembrede 2023Actualizado a las 12:42 h."
            match = re.search(r'(\d+)\sde\s([a-z]+)de\s(\d{4})Actualizado\sa\slas\s(\d{2}):(\d{2})', date_str)
            if match:
                day, month_str, year, hour, minute = match.groups()
                month = months[month_str]
                return datetime(int(year), month, int(day), int(hour), int(minute))
        
        # Retorna None si no coincide con ningún formato
        return None

    except Exception as e:
        print(f"Error al parsear fecha: {date_str} - {e}")
        return None

def generate_time_graph(titulo_compartido, periodico_seleccionado = None):

    noticias_filtradas = df[df['Titulo Compartido'] == titulo_compartido].copy()
    noticias_filtradas['Fecha'] = noticias_filtradas.apply(lambda row: parse_date(row['Fecha'], row['Periódico']), axis=1)

    # Eliminar filas con fechas nulas
    noticias_filtradas = noticias_filtradas.dropna(subset=['Fecha'])

    # Agrupar por periódico y obtener la primera publicación
    idx = noticias_filtradas.groupby('Periódico')['Fecha'].idxmin()
    noticias_filtradas = noticias_filtradas.loc[idx]

    # Asegurarse de que el DataFrame no esté vacío
    if noticias_filtradas.empty:
        return html.Div("No hay datos válidos para mostrar el gráfico.")

    # Ordenar los datos por fecha para una mejor visualización
    noticias_filtradas.sort_values('Fecha', inplace=True)

    # Asignar un valor constante para el eje Y
    noticias_filtradas['Bar_Height'] = 1
    
    # Aplica el mapeo a la columna 'Periódico' para crear una nueva columna con los nombres formateados
    noticias_filtradas['Nombre Formateado'] = noticias_filtradas['Periódico'].map(nombre_periodicos)
    
    # Asignar un color a cada barra basado en el periódico
    colores_barras = noticias_filtradas['Nombre Formateado'].map(colores_periodicos)

    if periodico_seleccionado != None:
        noticias_filtradas = noticias_filtradas[noticias_filtradas['Periódico'] == periodico_seleccionado]

    # Crear el gráfico de barras con Plotly Express
    fig = px.bar(
        noticias_filtradas,
        x='Fecha',
        y='Bar_Height',
        title='Primeros periódicos en publicar',
        text='Nombre Formateado',
        orientation='v',
        color=colores_barras,  # Usa los colores asignados
        color_discrete_map="identity"  # Indica a Plotly que use los colores exactos proporcionados
    )
    
    # Ajustar el layout del gráfico
    fig.update_layout(
        xaxis_title='Fecha',
        yaxis=dict(
            showticklabels=False,  # Oculta las etiquetas del eje Y
            title=None,  # Elimina el título del eje Y
        ),
        showlegend=False,  # Oculta la leyenda
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='closest'
    )

    # Ajustar el texto dentro de las barras y la información mostrada al pasar el ratón
    fig.update_traces(
        texttemplate='%{text}',  # Usa el texto de la nueva columna 'Nombre Formateado'
        textposition='inside',  # Esto ya debería centrar el texto si hay espacio suficiente
        textfont=dict(
            family="Arial, sans-serif",
            size=16,  # Puedes reducir el tamaño del texto para que encaje mejor
            color="white"
        ),
        textangle=90,  # Asegura que el texto esté horizontal
        hoverinfo='text',  # Solo muestra el texto al pasar el ratón
        insidetextanchor='middle'  # Esto centrará el texto verticalmente
    )

    # Ajustar la altura de la figura para que las barras no sean demasiado delgadas
    fig_height = max(400, len(noticias_filtradas) * 20)
    fig.update_layout(height=fig_height)

    return dcc.Graph(figure=fig)

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

def generate_media_spectrum(titulares_similares, periodico_seleccionado=None):

    orientaciones_politicas = {
        2: 'Derecha',
        1: 'Centro-Derecha',
        0: 'Centro',
        -1: 'Centro-Izquierda',
        -2: 'Izquierda',
        4: 'Deportivo',
        None: 'No Aplicable'
    }

    imagenes_periodicos = {
        'elmundoes': '/assets/elmundo.png', 
        'elpais': '/assets/elpais.png',
        'lavanguardia': '/assets/lavanguardia.png',
        'elconfidencial': '/assets/elconfidencial.png',
        'eldiarioes':'/assets/eldiarioes.png',
        'larazones':'/assets/larazon.png',
        'marca':'/assets/marca.png',
        'default': '/assets/default_image.png'
    }

    # Elimina el valor None del diccionario antes de ordenarlo
    orientaciones_politicas.pop(None)

    # Ordena las orientaciones políticas de izquierda a derecha
    orientaciones_ordenadas = sorted(orientaciones_politicas.items(), key=lambda x: x[0])

    # Agrupa los periódicos por su orientación política y evita repeticiones de logotipos
    periódicos_por_orientación = {}
    # Conjunto para rastrear periódicos ya representados
    periodicos_representados = set()

    for orientacion, orientacion_texto in orientaciones_ordenadas:
        # Crea una lista de logotipos únicos para la orientación política actual
        logos_orientacion = []

        # Filtra titulares por orientación política
        periodicos_orientacion = titulares_similares[titulares_similares['Orientación Política'] == orientacion]

        for periodico in periodicos_orientacion['Periódico'].unique():
            imagen_url = imagenes_periodicos.get(periodico, 'assets/default_image.png')
            if periodico_seleccionado is None or periodico == periodico_seleccionado:
                logo_link = html.A(
                    html.Img(src=imagen_url, style={'height': '60px', 'margin': '0 10px'})
                )
                logos_orientacion.append(logo_link)
                periodicos_representados.add(periodico)

        if logos_orientacion:
            orientacion_texto_div = html.P(orientacion_texto, style={'font-weight': 'bold', 'text-align': 'left'})
            logos_div = html.Div(
                children=logos_orientacion,
                style={'display': 'inline-block'}
            )

            periódicos_por_orientación[orientacion] = {
                'orientacion_texto': orientacion_texto_div,
                'logos': logos_div
            }

    # Crea los elementos finales con orientación política y logotipos únicos
    spectrum_divs = []
    for orientacion, data in periódicos_por_orientación.items():
        spectrum_divs.append(html.Div([data['orientacion_texto'], data['logos']]))

    # Contenedor para el espectro político
    spectrum_container = html.Div(
        children=spectrum_divs,
        style={'white-space': 'nowrap', 'overflow-x': 'auto'}  # Permite desplazamiento horizontal si es necesario
    )

    return spectrum_container

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

# Define el diseño de la aplicación
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Componente para manejar la URL
    dcc.Store(id='selected-newspaper-store'),
    html.Div(id='page-content'),  # Contenido de la página
    html.Div(id='all-squares',
        children=[
            generate_square(titulo_compartido, fecha)
            for titulo_compartido, fecha, _ in sorted(
                [
                    (titulo_compartido, fecha, len(df_similares.get_group(titulo_compartido)))
                    for titulo_compartido, fecha in zip(df['Titulo Compartido'], df['Fecha'])
                ],
                key=lambda x: x[2],  # Ordena por el número de noticias similares
                reverse=True  # Orden descendente
            )
            if titulo_compartido != "Ninguno" and titulo_compartido not in titulo_compartido_set and (titulo_compartido_set.add(titulo_compartido) or True)
        ]
    )
])

def default_content():
    return html.Div([
    dcc.Location(id='url', refresh=False),  # Componente para manejar la URL
    html.Div(id='page-content'),  # Contenido de la página
    html.Div(id='all-squares',
        children=[
            generate_square(titulo_compartido, fecha)
            for titulo_compartido, fecha, _ in sorted(
                [
                    (titulo_compartido, fecha, len(df_similares.get_group(titulo_compartido)))
                    for titulo_compartido, fecha in zip(df['Titulo Compartido'], df['Fecha'])
                ],
                key=lambda x: x[2],  # Ordena por el número de noticias similares
                reverse=True  # Orden descendente
            )
            if titulo_compartido != "Ninguno" and titulo_compartido not in titulo_compartido_set and (titulo_compartido_set.add(titulo_compartido) or True)
        ]
    )
])

# Callback que actualiza el store basado en la selección del usuario
@app.callback(
    Output('selected-newspaper-store', 'data'),
    [Input('newspaper-selector', 'value')]  # Suponiendo que 'newspaper-selector' es el ID del componente de selección
)
def update_selected_newspaper(selected_newspaper):
    return {'selected_newspaper': selected_newspaper}

# Define el callback para actualizar el contenido de la página
from datetime import datetime
import re
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import urllib.parse
import plotly.graph_objs as go
import plotly.express as px

# Cargar el DataFrame con las noticias similares desde un archivo Excel
df = pd.read_excel("noticiasSimilares.xlsx")

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

# Contar noticias y preparar datos para el gráfico
conteo_noticias = df_filtrado['Orientación Política'].value_counts().sort_index()
bar_data = go.Bar(
    x=conteo_noticias.index, 
    y=conteo_noticias.values, 
    marker=dict(color=conteo_noticias.values, colorscale='Viridis')
)

# Inicializar la aplicación Dash
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Ordenar el DataFrame por el número de ocurrencias de cada primer titular similar (descendente)
df_similares = df.groupby(['Titulo Compartido'])
titulo_compartido_set = set()

# Diccionario de meses en español
months = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
    'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

meses = {
    'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
}

# Función para procesar y convertir las fechas
def parse_date(date_str, periodico):
    try:
        # Dividir la cadena si contiene dos fechas
        if '  ' in date_str:
            date_str = date_str.split('  ')[0]       
        if periodico == 'elmundoes':
            # Formato: "Miércoles,15noviembre2023-12:38"
            match = re.search(r'(\d+)([a-z]+)(\d{4})-(\d{2}):(\d{2})', date_str)
            if match:
                day, month_str, year, hour, minute = match.groups()
                month = months[month_str]
                return datetime(int(year), month, int(day), int(hour), int(minute))
        
        elif periodico == 'elpais':
            # Formato: "15 nov 2023 - 12:34 CET"
            match = re.search(r'(\d{2})\s([a-z]+)\s(\d{4})\s-\s(\d{2}):(\d{2})', date_str)
            if match:
                day, month_str, year, hour, minute = match.groups()
                month = meses[month_str[:3]]
                return datetime(int(year), month, int(day), int(hour), int(minute))

        elif periodico == 'lavanguardia':
            # Formato: "15/11/2023 11:57"
            return datetime.strptime(date_str, '%d/%m/%Y %H:%M')

        elif periodico == 'elconfidencial':
            # Formato: "15/11/2023 - 11:44"
            return datetime.strptime(date_str, '%d/%m/%Y - %H:%M')

        elif periodico == 'eldiarioes':
            # Formato: "14 de noviembre de 202323:22h"
            match = re.search(r'(\d+)\sde\s([a-z]+)\sde\s(\d{4})\s*(\d{2}):(\d{2})h', date_str)
            if match:
                day, month_str, year, hour, minute = match.groups()
                month = months[month_str]
                return datetime(int(year), month, int(day), int(hour), int(minute))

        elif periodico == 'larazones':
            # Formato: "07.11.2023 00:45"
            return datetime.strptime(date_str, '%d.%m.%Y %H:%M')

        elif periodico == 'marca':
            # Formato: "15 de noviembrede 2023Actualizado a las 12:42 h."
            match = re.search(r'(\d+)\sde\s([a-z]+)de\s(\d{4})Actualizado\sa\slas\s(\d{2}):(\d{2})', date_str)
            if match:
                day, month_str, year, hour, minute = match.groups()
                month = months[month_str]
                return datetime(int(year), month, int(day), int(hour), int(minute))
        
        # Retorna None si no coincide con ningún formato
        return None

    except Exception as e:
        print(f"Error al parsear fecha: {date_str} - {e}")
        return None

def generate_time_graph(titulo_compartido, periodico_seleccionado = None):

    noticias_filtradas = df[df['Titulo Compartido'] == titulo_compartido].copy()
    noticias_filtradas['Fecha'] = noticias_filtradas.apply(lambda row: parse_date(row['Fecha'], row['Periódico']), axis=1)

    # Eliminar filas con fechas nulas
    noticias_filtradas = noticias_filtradas.dropna(subset=['Fecha'])

    # Agrupar por periódico y obtener la primera publicación
    idx = noticias_filtradas.groupby('Periódico')['Fecha'].idxmin()
    noticias_filtradas = noticias_filtradas.loc[idx]

    # Asegurarse de que el DataFrame no esté vacío
    if noticias_filtradas.empty:
        return html.Div("No hay datos válidos para mostrar el gráfico.")

    # Ordenar los datos por fecha para una mejor visualización
    noticias_filtradas.sort_values('Fecha', inplace=True)

    # Asignar un valor constante para el eje Y
    noticias_filtradas['Bar_Height'] = 1
    
    # Aplica el mapeo a la columna 'Periódico' para crear una nueva columna con los nombres formateados
    noticias_filtradas['Nombre Formateado'] = noticias_filtradas['Periódico'].map(nombre_periodicos)
    
    # Asignar un color a cada barra basado en el periódico
    colores_barras = noticias_filtradas['Nombre Formateado'].map(colores_periodicos)

    if periodico_seleccionado != None:
        noticias_filtradas = noticias_filtradas[noticias_filtradas['Periódico'] == periodico_seleccionado]

    # Crear el gráfico de barras con Plotly Express
    fig = px.bar(
        noticias_filtradas,
        x='Fecha',
        y='Bar_Height',
        title='Primeros periódicos en publicar',
        text='Nombre Formateado',
        orientation='v',
        color=colores_barras,  # Usa los colores asignados
        color_discrete_map="identity"  # Indica a Plotly que use los colores exactos proporcionados
    )
    
    # Ajustar el layout del gráfico
    fig.update_layout(
        xaxis_title='Fecha',
        yaxis=dict(
            showticklabels=False,  # Oculta las etiquetas del eje Y
            title=None,  # Elimina el título del eje Y
        ),
        showlegend=False,  # Oculta la leyenda
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='closest'
    )

    # Ajustar el texto dentro de las barras y la información mostrada al pasar el ratón
    fig.update_traces(
        texttemplate='%{text}',  # Usa el texto de la nueva columna 'Nombre Formateado'
        textposition='inside',  # Esto ya debería centrar el texto si hay espacio suficiente
        textfont=dict(
            family="Arial, sans-serif",
            size=16,  # Puedes reducir el tamaño del texto para que encaje mejor
            color="white"
        ),
        textangle=90,  # Asegura que el texto esté horizontal
        hoverinfo='text',  # Solo muestra el texto al pasar el ratón
        insidetextanchor='middle'  # Esto centrará el texto verticalmente
    )

    # Ajustar la altura de la figura para que las barras no sean demasiado delgadas
    fig_height = max(400, len(noticias_filtradas) * 20)
    fig.update_layout(height=fig_height)

    return dcc.Graph(figure=fig)

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

def generate_media_spectrum(titulares_similares, periodico_seleccionado=None):

    orientaciones_politicas = {
        2: 'Derecha',
        1: 'Centro-Derecha',
        0: 'Centro',
        -1: 'Centro-Izquierda',
        -2: 'Izquierda',
        4: 'Deportivo',
        None: 'No Aplicable'
    }

    imagenes_periodicos = {
        'elmundoes': '/assets/elmundo.png', 
        'elpais': '/assets/elpais.png',
        'lavanguardia': '/assets/lavanguardia.png',
        'elconfidencial': '/assets/elconfidencial.png',
        'eldiarioes':'/assets/eldiarioes.png',
        'larazones':'/assets/larazon.png',
        'marca':'/assets/marca.png',
        'default': '/assets/default_image.png'
    }

    # Elimina el valor None del diccionario antes de ordenarlo
    orientaciones_politicas.pop(None)

    # Ordena las orientaciones políticas de izquierda a derecha
    orientaciones_ordenadas = sorted(orientaciones_politicas.items(), key=lambda x: x[0])

    # Agrupa los periódicos por su orientación política y evita repeticiones de logotipos
    periódicos_por_orientación = {}
    # Conjunto para rastrear periódicos ya representados
    periodicos_representados = set()

    for orientacion, orientacion_texto in orientaciones_ordenadas:
        # Crea una lista de logotipos únicos para la orientación política actual
        logos_orientacion = []

        # Filtra titulares por orientación política
        periodicos_orientacion = titulares_similares[titulares_similares['Orientación Política'] == orientacion]

        for periodico in periodicos_orientacion['Periódico'].unique():
            imagen_url = imagenes_periodicos.get(periodico, 'assets/default_image.png')
            if periodico_seleccionado is None or periodico == periodico_seleccionado:
                logo_link = html.A(
                    html.Img(src=imagen_url, style={'height': '60px', 'margin': '0 10px'})
                )
                logos_orientacion.append(logo_link)
                periodicos_representados.add(periodico)

        if logos_orientacion:
            orientacion_texto_div = html.P(orientacion_texto, style={'font-weight': 'bold', 'text-align': 'left'})
            logos_div = html.Div(
                children=logos_orientacion,
                style={'display': 'inline-block'}
            )

            periódicos_por_orientación[orientacion] = {
                'orientacion_texto': orientacion_texto_div,
                'logos': logos_div
            }

    # Crea los elementos finales con orientación política y logotipos únicos
    spectrum_divs = []
    for orientacion, data in periódicos_por_orientación.items():
        spectrum_divs.append(html.Div([data['orientacion_texto'], data['logos']]))

    # Contenedor para el espectro político
    spectrum_container = html.Div(
        children=spectrum_divs,
        style={'white-space': 'nowrap', 'overflow-x': 'auto'}  # Permite desplazamiento horizontal si es necesario
    )

    return spectrum_container

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

# Define el diseño de la aplicación
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),  # Componente para manejar la URL
    dcc.Store(id='selected-newspaper-store'),
    html.Div(id='page-content'),  # Contenido de la página
    html.Div(id='all-squares',
        children=[
            generate_square(titulo_compartido, fecha)
            for titulo_compartido, fecha, _ in sorted(
                [
                    (titulo_compartido, fecha, len(df_similares.get_group(titulo_compartido)))
                    for titulo_compartido, fecha in zip(df['Titulo Compartido'], df['Fecha'])
                ],
                key=lambda x: x[2],  # Ordena por el número de noticias similares
                reverse=True  # Orden descendente
            )
            if titulo_compartido != "Ninguno" and titulo_compartido not in titulo_compartido_set and (titulo_compartido_set.add(titulo_compartido) or True)
        ]
    )
])

# Callback que actualiza el store basado en la selección del usuario
@app.callback(
    Output('selected-newspaper-store', 'data'),
    [Input('newspaper-selector', 'value')]  # Suponiendo que 'newspaper-selector' es el ID del componente de selección
)
def update_selected_newspaper(selected_newspaper):
    return {'selected_newspaper': selected_newspaper}

@app.callback(
    Output('page-content', 'children'),
    [Input('url', 'pathname'), State('selected-newspaper-store', 'data')],
    [State('page-content', 'children')]  # Añadir el estado actual del contenido de la página
)
def update_page_content(pathname, selected_newspaper_data, current_content):
    selected_newspaper = selected_newspaper_data.get('selected_newspaper') if selected_newspaper_data else None

    if not pathname.startswith('/similar/'):
        # Si la ruta no es '/similar/', retorna el contenido por defecto
        return [
            generate_square(titulo_compartido, fecha)
            for titulo_compartido, fecha, _ in sorted(
                [
                    (titulo_compartido, fecha, len(df_similares.get_group(titulo_compartido)))
                    for titulo_compartido, fecha in zip(df['Titulo Compartido'], df['Fecha'])
                ],
                key=lambda x: x[2], 
                reverse=True
            )
            if titulo_compartido != "Ninguno" and titulo_compartido not in titulo_compartido_set and (titulo_compartido_set.add(titulo_compartido) or True)
        ]

    # Si la ruta es '/similar/', pero la URL no ha cambiado, mantenemos el contenido actual
    if current_content and any('/similar/' in str(child) for child in current_content):
        return dash.no_update

    # Si la ruta es '/similar/' y la URL ha cambiado, genera un nuevo contenido
    common_title = urllib.parse.unquote(pathname.split('/')[-1])
    first_news = df[df['Titulo Compartido'] == common_title].iloc[0]
    fecha = first_news['Fecha']

    square = generate_square(common_title, fecha, selected_newspaper)
    similar_news = generate_similar_news(common_title, selected_newspaper)
    return [square] + similar_news


# Inicia la aplicación
if __name__ == '__main__':
    app.run_server(debug=True)