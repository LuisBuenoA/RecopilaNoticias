from datetime import datetime
import re

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