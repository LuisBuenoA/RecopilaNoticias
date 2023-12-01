from datetime import datetime
import re

# Diccionario para convertir nombres de meses en español a números
months = {
    'enero': 1, 'febrero': 2, 'marzo': 3, 'abril': 4, 'mayo': 5, 'junio': 6,
    'julio': 7, 'agosto': 8, 'septiembre': 9, 'octubre': 10, 'noviembre': 11, 'diciembre': 12
}

meses = {
    'ene': 1, 'feb': 2, 'mar': 3, 'abr': 4, 'may': 5, 'jun': 6,
    'jul': 7, 'ago': 8, 'sep': 9, 'oct': 10, 'nov': 11, 'dic': 12
}

# Función para convertir cadenas de texto con fechas a objetos datetime de Python
def parse_date(date_str, periodico):
    try:
        # Manejar casos donde la cadena de fecha contiene dos fechas separadas por dos espacios
        if '  ' in date_str:
            date_str = date_str.split('  ')[0]

        # Parsear fechas según el formato específico de cada periódico
        if periodico == 'elmundoes':
            # Formato de fecha para el periódico "El Mundo"
            match = re.search(r'(\d+)([a-z]+)(\d{4})-(\d{2}):(\d{2})', date_str)
            if match:
                day, month_str, year, hour, minute = match.groups()
                month = months[month_str]
                return datetime(int(year), month, int(day), int(hour), int(minute))
        
        elif periodico == 'elpais':
            # Formato de fecha para el periódico "El País"
            match = re.search(r'(\d{2})\s([a-z]+)\s(\d{4})\s-\s(\d{2}):(\d{2})', date_str)
            if match:
                day, month_str, year, hour, minute = match.groups()
                month = meses[month_str[:3]]
                return datetime(int(year), month, int(day), int(hour), int(minute))

        elif periodico == 'lavanguardia':
            # Formato de fecha para "La Vanguardia"
            return datetime.strptime(date_str, '%d/%m/%Y %H:%M')

        elif periodico == 'elconfidencial':
            # Formato de fecha para "El Confidencial"
            return datetime.strptime(date_str, '%d/%m/%Y - %H:%M')

        elif periodico == 'eldiarioes':
            # Formato de fecha para "El Diario"
            match = re.search(r'(\d+)\sde\s([a-z]+)\sde\s(\d{4})\s*(\d{2}):(\d{2})h', date_str)
            if match:
                day, month_str, year, hour, minute = match.groups()
                month = months[month_str]
                return datetime(int(year), month, int(day), int(hour), int(minute))

        elif periodico == 'larazones':
            # Formato de fecha para "La Razón"
            return datetime.strptime(date_str, '%d.%m.%Y %H:%M')

        elif periodico == 'marca':
            # Formato de fecha para "Marca"
            match = re.search(r'(\d+)\sde\s([a-z]+)de\s(\d{4})Actualizado\sa\slas\s(\d{2}):(\d{2})', date_str)
            if match:
                day, month_str, year, hour, minute = match.groups()
                month = months[month_str]
                return datetime(int(year), month, int(day), int(hour), int(minute))
        
        # Retorna None si la cadena de fecha no coincide con ningún formato conocido
        return None

    except Exception as e:
        # Manejar cualquier error que ocurra durante el parseo de la fecha
        print(f"Error al parsear fecha: {date_str} - {e}")
        return None