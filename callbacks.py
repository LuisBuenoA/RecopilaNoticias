from dash.dependencies import Input, Output, State
from generate import generate_square, generate_similar_news
from data import df,df_similares, titulo_compartido_set
import dash
import urllib.parse

def register_callbacks(app):
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