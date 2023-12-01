from dash import dcc, html
import plotly.express as px
from utils import parse_date
from data import df, nombre_periodicos, colores_periodicos
from datetime import timedelta

def generate_scatter_titles():
    """
    Función para generar un gráfico de dispersión de titulares con datos similares.
    Este gráfico visualiza la relación entre la fecha de publicación, 
    el número de noticias similares y la diversidad de periódicos.
    """
    # Filtrado de noticias con titulares compartidos
    noticias_filtradas = df[df['Titulo Compartido'] != 'Ninguno'].copy()

    # Conversión de fechas al formato adecuado
    noticias_filtradas['Fecha'] = noticias_filtradas.apply(lambda row: parse_date(row['Fecha'], row['Periódico']), axis=1)

    # Agrupación y cálculo de estadísticas relevantes por titular compartido
    grouped = noticias_filtradas.groupby('Titulo Compartido').agg(
        fecha_minima=('Fecha', 'min'),
        conteo_noticias=('Titulo Compartido', 'size'),
        periódicos_distintos=('Periódico', 'nunique')
    ).reset_index()

    # Identificación del titular con la mayor cantidad de noticias similares
    top_titular = grouped[grouped['conteo_noticias'] == grouped['conteo_noticias'].max()]

    # Creación del gráfico de dispersión usando Plotly Express
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
        title='Relación entre Fecha de Publicación y Número de Noticias Similares'
    )

    # Añadir anotación para el titular más destacado
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
            ax=-550,
            ay=-30,
            standoff=15,
            arrowcolor="darkblue",
            arrowsize=1,
            arrowwidth=1,
            bordercolor="#c7c7c7",
            borderwidth=1,
            borderpad=4,
            bgcolor="#ffffff",
            opacity=0.8
        )

    # Ajustes finales del layout del gráfico
    fig.update_layout(
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            tickvals=[0, 5, 10, 15, 20]
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return dcc.Graph(figure=fig)

def generate_newspaper_graph():
    """
    Función para generar un gráfico de barras que muestra el número de noticias por periódico,
    diferenciando entre noticias con y sin titulares similares.
    """
    # Categorización de noticias basada en la existencia de titulares similares
    df['Categoría'] = df['Titulo Compartido'].apply(lambda x: 'Con Titulares Similares' if x != 'Ninguno' else 'Sin Titulares Similares')

    # Agrupación y conteo de noticias por periódico y categoría
    newspaper_counts = df.groupby(['Periódico', 'Categoría']).size().reset_index(name='Número de Noticias')

    # Creación del gráfico de barras
    fig = px.bar(
        newspaper_counts,
        x='Periódico',
        y='Número de Noticias',
        color='Categoría',
        title='Distribución de Noticias por Periódico y Categoría',
        barmode='stack',
        color_discrete_map={'Con Titulares Similares': 'darkblue', 'Sin Titulares Similares': 'darkgrey'}
    )

    # Ajustes finales del layout del gráfico
    fig.update_layout(
        xaxis_title="",
        showlegend=True,
        xaxis={'categoryorder':'total descending'},
        yaxis=dict(
            title=None,
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            tickvals=[0, 50, 100, 150, 200]
        ),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )

    return dcc.Graph(figure=fig)

def generate_time_graph(titulo_compartido, periodico_seleccionado=None):
    """
    Genera un gráfico de barras para visualizar cuándo y por qué periódicos se publicó un titular compartido.
    """

    # Filtra las noticias por el titular compartido y convierte las fechas
    noticias_filtradas = df[df['Titulo Compartido'] == titulo_compartido].copy()
    noticias_filtradas['Fecha'] = noticias_filtradas.apply(lambda row: parse_date(row['Fecha'], row['Periódico']), axis=1)

    # Elimina filas sin fecha y agrupa por periódico para obtener la primera publicación
    noticias_filtradas = noticias_filtradas.dropna(subset=['Fecha'])
    idx = noticias_filtradas.groupby('Periódico')['Fecha'].idxmin()
    noticias_filtradas = noticias_filtradas.loc[idx]

    # Verifica si hay datos para mostrar
    if noticias_filtradas.empty:
        return html.Div("No hay datos válidos para mostrar el gráfico.")

    # Ordena las noticias por fecha
    noticias_filtradas.sort_values('Fecha', inplace=True)

    # Asigna un valor constante para el eje Y y mapea los nombres de los periódicos a nombres formateados
    noticias_filtradas['Bar_Height'] = 1
    noticias_filtradas['Nombre Formateado'] = noticias_filtradas['Periódico'].map(nombre_periodicos)

    # Asignar un color a cada barra basado en el periódico
    colores_barras = noticias_filtradas['Nombre Formateado'].map(colores_periodicos)

    # Filtra las noticias si se ha seleccionado un periódico específico
    if periodico_seleccionado:
        noticias_filtradas = noticias_filtradas[noticias_filtradas['Periódico'] == periodico_seleccionado]

 # Crea el gráfico de barras con Plotly Express
    fig = px.bar(
        noticias_filtradas,
        x='Fecha',
        y='Bar_Height',
        title='Primeros periódicos en publicar',
        text='Nombre Formateado',
        orientation='v',
        color=colores_barras,
        color_discrete_map="identity"
    )

    # Ajusta el layout del gráfico
    fig.update_layout(
        yaxis=dict(
            showticklabels=False,
            title=None,
            showgrid=True,
            gridcolor='rgba(128,128,128,0.2)',
            tickvals=[0.01, 0.25, 0.5, 0.75, 1]
        ),
        showlegend=False,
        margin=dict(l=50, r=50, t=50, b=50),
        hovermode='closest',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(
            title=None,
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1d", step="day", stepmode="backward"),
                    dict(count=7, label="1w", step="day", stepmode="backward"),
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(step="all")
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type="date"
        )
    )

    # Ajusta el texto y la información de las barras
    fig.update_traces(
        texttemplate='%{text}',
        textposition='inside',
        textfont=dict(
            family="Arial, sans-serif",
            size=16,
            color="white"
        ),
        textangle=90,
        hoverinfo='text',
        insidetextanchor='middle'
    )

    # Ajusta la altura de la figura
    fig.update_layout(height=max(300, len(noticias_filtradas) * 20))

    return dcc.Graph(figure=fig)

def generate_media_spectrum(titulares_similares, periodico_seleccionado=None):
    """
    Crea una representación visual del espectro político de los medios de comunicación
    basada en los titulares similares y la orientación política de cada periódico.
    """

    # Diccionario que asocia orientaciones políticas con su descripción
    orientaciones_politicas = {
        2: 'Derecha',
        1: 'Centro-Derecha',
        0: 'Centro',
        -1: 'Centro-Izquierda',
        -2: 'Izquierda',
        4: 'Deportivo',
        None: 'No Aplicable'
    }

    # Diccionario con los logos de los periódicos
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

    # Ordenar las orientaciones políticas para su presentación
    orientaciones_politicas.pop(None)

    # Ordena las orientaciones políticas de izquierda a derecha
    orientaciones_ordenadas = sorted(orientaciones_politicas.items(), key=lambda x: x[0])

    # Conjunto para rastrear periódicos ya representados
    periodicos_representados = set()

    # Agrupa los periódicos por su orientación política
    periódicos_por_orientación = {}
    for orientacion, orientacion_texto in orientaciones_ordenadas:
        logos_orientacion = []

        # Filtra titulares por orientación política
        periodicos_orientacion = titulares_similares[titulares_similares['Orientación Política'] == orientacion]

        # Crear una lista de logos únicos para cada orientación política
        for periodico in periodicos_orientacion['Periódico'].unique():
            imagen_url = imagenes_periodicos.get(periodico, 'assets/default_image.png')
            if periodico_seleccionado is None or periodico == periodico_seleccionado:
                logo_link = html.A(
                    html.Img(src=imagen_url, style={'height': '60px', 'margin': '0 0 0 20px'})
                )
                logos_orientacion.append(logo_link)
                periodicos_representados.add(periodico)

        # Añadir la orientación política y sus logos al diccionario
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

    # Compilar los elementos en un contenedor
    spectrum_divs = []
    for orientacion, data in periódicos_por_orientación.items():
        spectrum_divs.append(html.Div([data['orientacion_texto'], data['logos']], style={'margin': '1px 30px 1px 30px'}))

    # Crear el contenedor final para el espectro político
    spectrum_container = html.Div(
        children=spectrum_divs,
        style={'white-space': 'nowrap', 'overflow-x': 'auto'} 
    )

    return spectrum_container