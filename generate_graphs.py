from dash import dcc, html
import plotly.express as px
from utils import parse_date
from data import df, nombre_periodicos, colores_periodicos

def generate_scatter_titles():
    # Filtrar las noticias que tienen un título compartido (no 'Ninguno')
    noticias_filtradas = df[df['Titulo Compartido'] != 'Ninguno'].copy()

    # Aplicar la función parse_date para convertir la columna 'Fecha'
    noticias_filtradas['Fecha'] = noticias_filtradas.apply(lambda row: parse_date(row['Fecha'], row['Periódico']), axis=1)

    # Agrupar por 'Titulo Compartido' y obtener la fecha más antigua, el conteo de noticias y el número de periódicos distintos
    grouped = noticias_filtradas.groupby('Titulo Compartido').agg(
        fecha_minima=('Fecha', 'min'),
        conteo_noticias=('Titulo Compartido', 'size'),
        periódicos_distintos=('Periódico', 'nunique')  # Contar el número de periódicos distintos
    ).reset_index()

    # Encontrar el titular con más noticias similares
    top_titular = grouped[grouped['conteo_noticias'] == grouped['conteo_noticias'].max()]

    # Crear el gráfico de dispersión
    fig = px.scatter(
        grouped,
        x='fecha_minima',
        y='conteo_noticias',
        size='periódicos_distintos',
        color_discrete_sequence=['darkblue'],
        hover_data=['Titulo Compartido'],
        labels={
            'fecha_minima': 'Fecha',
            'conteo_noticias': 'Número de Noticias',
            'periódicos_distintos': 'Periódicos Distintos'
        },
        title=''
    )

    # Añadir anotación para el titular con más noticias similares
    for i in top_titular.index:
        texto_anotacion = (
            f"{top_titular.loc[i, 'Titulo Compartido']}<br>"
            f"Fecha: {top_titular.loc[i, 'fecha_minima']:%Y-%m-%d}<br>"
            f"Noticias: {top_titular.loc[i, 'conteo_noticias']}<br>"
            f"Periódicos Distintos: {top_titular.loc[i, 'periódicos_distintos']}"
        )
        fig.add_annotation(
            x=top_titular.loc[i, 'fecha_minima'],
            y=top_titular.loc[i, 'conteo_noticias'],
            text=texto_anotacion,
            showarrow=True,
            arrowhead=1,
            ax=-550,  # Desplazar la punta de la flecha 50px a la izquierda del punto
            ay=-30,  # Desplazar la punta de la flecha 50px arriba del punto
            standoff=15,  # Distancia que la punta de la flecha se mantendrá alejada del punto
            arrowcolor="darkblue",
            arrowsize=1,
            arrowwidth=1,
            bordercolor="#c7c7c7",
            borderwidth=1,
            borderpad=4,
            bgcolor="#ffffff",
            opacity=0.8
        )

    # Ajustar el layout según sea necesario
    fig.update_layout(
        xaxis=dict(
            showgrid=True,  # Muestra las líneas de la cuadrícula horizontal
            gridcolor='rgba(128,128,128,0.2)'  # El color y la transparencia de la cuadrícula
        ),
        yaxis=dict(
            showgrid=True,  # Muestra las líneas de la cuadrícula horizontal
            gridcolor='rgba(128,128,128,0.2)',  # El color y la transparencia de la cuadrícula
            tickvals=[ 0, 5, 10, 15, 20]
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return dcc.Graph(figure=fig)

def generate_newspaper_graph():
    # Categorizar cada noticia
    df['Categoría'] = df['Titulo Compartido'].apply(lambda x: 'Con Titulares Similares' if x != 'Ninguno' else 'Sin Titulares Similares')

    # Agrupar por periódico y categoría, y contar
    newspaper_counts = df.groupby(['Periódico', 'Categoría']).size().reset_index(name='Número de Noticias')

    # Crear el gráfico de barras
    fig = px.bar(
        newspaper_counts,
        x='Periódico',
        y='Número de Noticias',
        color='Categoría',
        title='Número de Noticias por Periódico',
        barmode='stack',  # Apilar las barras
        color_discrete_map={'Con Titulares Similares': 'darkblue', 'Sin Titulares Similares': 'darkgrey'}  # Colores personalizados
    )


    # Ajustar el layout según sea necesario
    fig.update_layout(
        xaxis_title="",  # Eliminar el título del eje X
        showlegend=True,  # Mostrar leyenda para distinguir categorías
        xaxis={'categoryorder':'total descending'},
        yaxis=dict(
            title=None,
            showgrid=True,  # Muestra las líneas de la cuadrícula horizontal
            gridcolor='rgba(128,128,128,0.2)',  # El color y la transparencia de la cuadrícula
            tickvals=[ 0, 50, 100, 150, 200]
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return dcc.Graph(figure=fig)

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
        xaxis=dict(
            title=None,
        ),
        yaxis=dict(
            showticklabels=False,  # Oculta las etiquetas del eje Y
            title=None,  # Elimina el título del eje Y
            showgrid=True,  # Muestra las líneas de la cuadrícula horizontal
            gridcolor='rgba(128,128,128,0.2)',  # El color y la transparencia de la cuadrícula
            tickvals=[ 0.01, 0.25, 0.5, 0.75, 1]
        ),
        showlegend=False,  # Oculta la leyenda
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='closest',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
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
    fig_height = max(300, len(noticias_filtradas) * 20)
    fig.update_layout(height=fig_height)

    return dcc.Graph(figure=fig)

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
                    html.Img(src=imagen_url, style={'height': '60px', 'margin': '0 0 0 20px'})
                )
                logos_orientacion.append(logo_link)
                periodicos_representados.add(periodico)

        if logos_orientacion:
            orientacion_texto_div = html.P(orientacion_texto, style={'font-weight': 'bold', 'text-align': 'left', 'margin': '20px 0 20px 20px'})
            logos_div = html.Div(
                children=logos_orientacion,
                style={'display': 'inline-block', 'margin': '1px 30px 1px 30px'}
            )

            periódicos_por_orientación[orientacion] = {
                'orientacion_texto': orientacion_texto_div,
                'logos': logos_div
            }

    # Crea los elementos finales con orientación política y logotipos únicos
    spectrum_divs = []
    for orientacion, data in periódicos_por_orientación.items():
        spectrum_divs.append(html.Div([data['orientacion_texto'], data['logos']], style={'margin': '1px 30px 1px 30px'}))

    # Contenedor para el espectro político
    spectrum_container = html.Div(
        children=spectrum_divs,
        style={'white-space': 'nowrap', 'overflow-x': 'auto'}  # Permite desplazamiento horizontal si es necesario
    )

    return spectrum_container