from dash import html, dcc
from generate import generate_square
from data import df_similares, titulo_compartido_set, df

def create_layout():
    return html.Div([
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