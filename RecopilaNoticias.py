import requests
import re
from bs4 import BeautifulSoup
from datetime import datetime
import pandas as pd

def obtener_articulos(fecha, url):
    titulo_ant = ''
    guardar=0
    url_el_mundo = 'https://elmundo.es/'
    url_el_pais = 'https://elpais.com/'
    url_la_vanguardia = 'https://lavanguardia.com/'
    url_abc = 'https://abc.es/'
    url_el_confidencial = 'https://elconfidencial.com/'
    url_la_voz_de_galicia = 'https://lavozdegalicia.es/'
    url_el_diario = 'https://eldiario.es/'
    url_publico = 'https://publico.es/'
    url_el_espanol = 'https://elespanol.com/'
    url_la_razon = 'https://larazon.es/'
    url_marca = 'https://marca.com/'
    url_as = 'https://as.com/'

    # Crear una lista para almacenar los datos
    datos = []
    try:
        # Descargar la página web
        response = requests.get(url, verify = False)
        response.raise_for_status()  # Esto verifica si hay un error en la respuesta
        page_content = response.content

        # Analizar la página web
        soup = BeautifulSoup(page_content, 'html.parser')

        # Encontrar todos los enlaces a los artículos
        enlaces = soup.find_all('a', href=True)
        
        for enlace in enlaces:
            # Filtrar los enlaces que parecen ser artículos
            if (fecha in enlace['href'] or (url == url_el_diario and '.html' in enlace['href']) or (url == url_publico and ('#md=modulo-portada-bloque:' in enlace['href']) )) and ('www.amazon.' not in enlace['href']) and ('www.mujerhoy.' not in enlace['href']) and ('venagalicia.gal' not in enlace['href']) and ('apple.com' not in enlace['href']) and ('magas.elespanol' not in enlace['href'] ) and ('mundodeportivo.com' not in enlace['href'])  and ('eldiarioar.com' not in enlace['href'] ) and ('//branded.' not in enlace['href'] ) and ('.com/vela/' not in enlace['href'] ) and ('.htmlhttps://' not in enlace['href'] ):
                # Construir el enlace completo al artículo
                if url == url_el_mundo or url == url_abc or url == url_el_confidencial or 'https://' in enlace['href'] or url == url_la_razon or url == url_marca:
                    enlace_articulo = enlace['href']
                elif url == url_el_pais:
                    enlace_articulo = url + enlace['href']
                elif url == url_publico or url == url_la_vanguardia or url == url_la_voz_de_galicia or url == url_el_diario or url == url_el_espanol:
                    url = url.rstrip('/')
                    enlace_articulo = url + enlace['href']
                else:
                    enlace_articulo = url + enlace['href']

                # Descargar y analizar la página del artículo
                response_articulo = requests.get(enlace_articulo)
                response_articulo.raise_for_status()  # Manejar posibles errores en la descarga
                page_content_articulo = response_articulo.content
                soup_articulo = BeautifulSoup(page_content_articulo, 'html.parser')
                # Extraer el título del artículo
                titulo = soup_articulo.find('h1')
                if titulo and titulo_ant != titulo:
                    
                    titulo_texto = titulo.text

                    # Extraer la fecha y hora del artículo si existe
                    if url == url_el_espanol:
                        datoFecha = soup_articulo.find('span', class_='article-header__time')
                        fecha_texto = datoFecha.text.replace('\n', '').replace('Actualizado:','').strip() if datoFecha else "NA"
                    else:
                        datoFecha = soup_articulo.find('time')
                        fecha_texto = datoFecha.text.replace('\n', '').replace('Actualizado:','').strip() if datoFecha else "NA"

                    # Extraer el cuerpo del artículo si existe
                    if url == url_el_mundo:
                        cuerpo = soup_articulo.find('div', class_='ue-l-article__body')
                    elif url == url_el_pais:
                        cuerpo = soup_articulo.find('div', class_='a_c')
                    elif url == url_la_vanguardia:
                        cuerpo = soup_articulo.find('div', class_='article-modules')
                    elif url == url_abc:
                        cuerpo = soup_articulo.find('div', class_='voc-d')
                    elif url == url_el_confidencial:
                        cuerpo = soup_articulo.find('div', class_='newsType__content')
                    elif url == url_la_voz_de_galicia or 'https://www.lavozdegalicia' in enlace['href']:
                        cuerpo = soup_articulo.find('div', class_='col sz-dk-67 txt-blk')
                        if cuerpo is None:
                            cuerpo = soup_articulo.find('div', class_='col')
                    elif url == url_el_diario:
                        cuerpo = soup_articulo.find('div', class_='partner-wrapper article-page__body-row')
                    elif url == url_publico:
                        cuerpo = soup_articulo.find('div', class_='article-body')
                        if cuerpo is None:
                            cuerpo = soup_articulo.find('div', class_='content-inside')
                    elif url == url_la_razon:
                        cuerpo = soup_articulo.find('div', class_='article-main__content')
                    elif url == url_marca:
                        cuerpo = soup_articulo.find('div', class_='ue-c-article__body')
                    elif url == url_as:
                        cuerpo = soup_articulo.find('div', class_='art__bo is-unfolded')
                    elif url == url_el_espanol or 'https://' in enlace['href']:
                        print(enlace['href'])
                        cuerpo = soup_articulo.find('div', class_='article-body__content')
                        if cuerpo is None:
                            cuerpo = soup_articulo.find('div', class_='article-body-content')
                            print(cuerpo)
                        print(cuerpo)
                    else:
                        cuerpo = soup_articulo.find('div', class_='a_c')
                    
                    if cuerpo:
                        parrafos = cuerpo.find_all('p')
                        cuerpo_texto = '\n'.join(parrafo.text for parrafo in parrafos)
                        
                        # Quitar intros duplicados
                        cuerpo_texto = re.sub(r'\n{2,}', '\n', cuerpo_texto)
                        
                        periodico = url.replace("https://", "").replace(".", "").replace("/", "").replace("com", "").replace(":", "")
                        # Agregar los datos a la lista
                        datos.append({'Título': titulo_texto, 'Cuerpo': cuerpo_texto, 'Fecha': fecha_texto, 'Periódico': periodico, 'Enlace': enlace_articulo})

                        guardar=1

                    titulo_ant = titulo
        print(guardar)
        # Crear un DataFrame a partir de los datos
        df = pd.DataFrame(datos)

        # Guardar el DataFrame en un archivo Excel
        if guardar == 1:
            excel_filename = (
                url.replace("https://", "")
                .replace(".", "")
                .replace("/", "")
                .replace("com", "")
                .replace(":", "")
                + '.xlsx'
            )
            df.to_excel(excel_filename, index=False)
    except requests.exceptions.HTTPError as http_err:
        print(f'Error HTTP: {http_err}')
    except Exception as err:
        print(f'Otro error: {err}')



# Ejemplo de uso
fecha_formateada = '2023'
url_el_mundo = 'https://elmundo.es/'
url_el_pais = 'https://elpais.com/'
url_la_vanguardia = 'https://lavanguardia.com/'
#url_abc = 'https://abc.es/' #Muy protegido de webscraping
url_el_confidencial = 'https://elconfidencial.com/'
url_la_voz_de_galicia = 'https://lavozdegalicia.es/'
url_el_diario = 'https://eldiario.es/'
#url_publico = 'https://publico.es/' #Error al hacer muchos requests
#url_el_espanol = 'https://elespanol.com/' #antes iba pero ya no
url_la_razon = 'https://larazon.es/'
url_marca = 'https://marca.com/'
#url_as = 'https://as.com/' #Lógica de enlaces muy distinta del resto

urls = []
urls.extend([url_el_mundo, url_el_pais, url_la_vanguardia, url_el_confidencial, url_la_voz_de_galicia, url_el_diario, url_la_razon, url_marca])

for url in urls:
    print('Periodico:', url)
    obtener_articulos(fecha_formateada, url)
    print('-' * 50)
