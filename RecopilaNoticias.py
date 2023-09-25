import requests
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

def obtener_articulos(fecha, url):
    titulo_ant = ''
    # Crear una lista para almacenar los datos
    datos = []

    # Descargar la página web
    response = requests.get(url)
    page_content = response.content

    # Analizar la página web
    soup = BeautifulSoup(page_content, 'html.parser')

    # Encontrar todos los enlaces a los artículos
    enlaces = soup.find_all('a', href=True)
    for enlace in enlaces:
        # Filtrar los enlaces que parecen ser artículos
        if fecha in enlace['href']:

            # Construir el enlace completo al artículo
            enlace_articulo = url + enlace['href']

            # Descargar y analizar la página del artículo
            response_articulo = requests.get(enlace_articulo)
            page_content_articulo = response_articulo.content
            soup_articulo = BeautifulSoup(page_content_articulo, 'html.parser')

            # Extraer el título del artículo
            titulo = soup_articulo.find('h1')
            if titulo and titulo_ant != titulo:
                print('Título:', titulo.text)
                titulo_texto = titulo.text

                # Extraer la fecha y hora del artículo si existe
                datoFecha = soup_articulo.find('time')
                fecha_texto = datoFecha.text if datoFecha else "No se encontró la fecha"

                # Extraer el cuerpo del artículo si existe
                cuerpo = soup_articulo.find('div', class_='a_c')
                if cuerpo:
                    parrafos = cuerpo.find_all('p')
                    cuerpo_texto = '\n'.join(parrafo.text for parrafo in parrafos)

                    # Agregar los datos a la lista
                    datos.append({'Título': titulo_texto, 'Cuerpo': cuerpo_texto, 'Dia y hora': fecha_texto})

                print('-' * 50)
                titulo_ant = titulo

    # Crear un DataFrame a partir de los datos
    df = pd.DataFrame(datos)

    # Obtener la fecha y hora actual
    fecha_hora_actual = datetime.now()

    # Formatear la fecha y hora como una cadena (sin microsegundos)
    fecha_hora_formateada = fecha_hora_actual.strftime('%Y-%m-%d_%H-%M-%S')

    # Guardar el DataFrame en un archivo Excel
    excel = (
        url.replace("https://", "")
        .replace(".", "")
        .replace("/", "")
        .replace("com", "")
        .replace(":", "-")
        + '_'
        + fecha_hora_formateada
        + '.xlsx'
    )

    df.to_excel(excel, index=False)


# Ejemplo de uso
fecha_formateada = '2023'
url_el_pais = 'https://elpais.com/'
obtener_articulos(fecha_formateada, url_el_pais)
