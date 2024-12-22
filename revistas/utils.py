import requests
import xml.etree.ElementTree as ET
from .models import Articulo, Revista
import unicodedata
from django.utils.timezone import now
from .models import Revista, Articulo
from datetime import datetime, date

def formatear_fecha(fecha):
    """
    Convierte una fecha en formato 'YYYY-MM-DD' o 'YYYY-MM-DDTHH:MM:SSZ' a un objeto `datetime.date`.
    """
    if isinstance(fecha, date):  # Verifica correctamente si es un objeto `date`
        return fecha
    if isinstance(fecha, str):  # Verifica que sea una cadena antes de intentar convertir
        try:
            # Intenta formatos específicos
            if "T" in fecha:
                return datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%SZ").date()
            else:
                return datetime.strptime(fecha, "%Y-%m-%d").date()
        except ValueError:
            print(f"Error al formatear fecha: {fecha}")
            return None
    print(f"Tipo no esperado para la fecha: {type(fecha)}")
    return None

def transfer_publisher_to_revista():
    """
    Transfiere el valor del campo publisher del primer artículo
    relacionado a la revista correspondiente.
    """
    revistas = Revista.objects.all()

    for revista in revistas:
        # Cambia 'revista' por 'fuente' en el filtro
        articulo = Articulo.objects.filter(fuente=revista).exclude(publisher__isnull=True).first()

        if articulo and articulo.publisher:
            # Actualizar el campo publisher en la revista si no está definido
            if not revista.publisher:
                revista.publisher = articulo.publisher
                revista.save()
                print(f"Actualizado publisher de la revista '{revista.repository_name}' a '{articulo.publisher}'")
            else:
                print(f"La revista '{revista.repository_name}' ya tiene un publisher definido: '{revista.publisher}'")

def limpiar_texto(texto, max_length=None):
    """
    Limpia caracteres especiales no válidos (como emojis) para evitar errores al guardar en MySQL.
    """
    if texto:
        texto_limpio = ''.join(c for c in texto if unicodedata.category(c) != 'Cs')  # Elimina caracteres no válidos
        if max_length and len(texto_limpio) > max_length:
            return texto_limpio[:max_length]
        return texto_limpio
    return "No disponible"


def cosechar_datos_directo(url, metadata_prefix, revista_id):
    """
    Descarga y almacena todos los artículos desde un servidor OAI-PMH.
    """
    try:
        revista = Revista.objects.get(id=revista_id)
    except Revista.DoesNotExist:
        raise ValueError(f"La revista con id {revista_id} no existe.")

    print(f"Iniciando la cosecha desde: {url} con prefijo: {metadata_prefix}")
    base_url = f"{url}?verb=ListRecords"
    next_token = None

    while True:
        # Construcción de la URL de solicitud
        if next_token:
            request_url = f"{base_url}&resumptionToken={next_token}"
        else:
            request_url = f"{base_url}&metadataPrefix={metadata_prefix}"

        print(f"Realizando solicitud a: {request_url}")
        response = requests.get(request_url)

        if response.status_code != 200:
            raise Exception(f"Error al conectar con {url}. Código de estado: {response.status_code}")

        print(f"Respuesta XML recibida:\n{response.text[:500]}... [truncado]")

        try:
            registros, next_token = procesar_respuesta(response.text)
        except Exception as e:
            print(f"Error al procesar la respuesta: {e}")
            break

        print(f"Registros cosechados en este lote: {len(registros)}")

        for registro in registros:
            # Crear o actualizar un artículo
            articulo, created = Articulo.objects.update_or_create(
                identifier=registro['identifier'],
                defaults={
                    "fuente": revista,  # Relación con la revista
                    "datestamp": formatear_fecha(registro['datestamp']),
                    "set_spec": limpiar_texto(registro.get('set_spec')),
                    "title_es": limpiar_texto(registro.get('title_es')),
                    "title_en": limpiar_texto(registro.get('title_en')),
                    "creator": limpiar_texto(registro.get('creator')),
                    "publisher": limpiar_texto(registro.get('publisher')),
                    "type": limpiar_texto(registro.get('type')),
                    "format": limpiar_texto(registro.get('format')),
                    "identifier_url": registro.get('identifier_url'),
                    "language": limpiar_texto(registro.get('language')),
                    "relation": limpiar_texto(registro.get('relation')),
                    "coverage": limpiar_texto(registro.get('coverage')),
                    "rights": limpiar_texto(registro.get('rights')),
                    "date": formatear_fecha(registro.get('date')),
                    "subjects_es": "; ".join(registro.get('subjects_es', [])),
                    "subjects_en": "; ".join(registro.get('subjects_en', [])),
                    "descriptions_es": "; ".join(registro.get('descriptions_es', [])),
                    "descriptions_en": "; ".join(registro.get('descriptions_en', [])),
                    "sources": "; ".join(registro.get('sources', [])),
                }
            )
            print(f"Artículo {'creado' if created else 'actualizado'}: {registro.get('title_es')}")

        if not next_token:
            print("No hay más registros para cosechar.")
            break

    revista.last_harvest_date = now()
    revista.save()

    print("Cosecha completada.")
    transfer_publisher_to_revista()


def procesar_respuesta(xml_response):
    """
    Procesa la respuesta XML y devuelve los registros en un formato limpio utilizando Dublin Core.
    """
    registros = []
    namespaces = {
    "oai": "http://www.openarchives.org/OAI/2.0/",
    "dc": "http://purl.org/dc/elements/1.1/",
    "oai_dc": "http://www.openarchives.org/OAI/2.0/oai_dc/",
    "xml": "http://www.w3.org/XML/1998/namespace",  # Agregamos el prefijo xml
}

    try:
        root = ET.fromstring(xml_response)
    except ET.ParseError as e:
        raise ValueError(f"Error al analizar el XML: {e}")

    for record in root.findall("oai:ListRecords/oai:record", namespaces):
        header = record.find("oai:header", namespaces)
        metadata = record.find("oai:metadata/oai_dc:dc", namespaces)

        if header is None or metadata is None:
            print("Registro inválido encontrado. Saltando...")
            continue

        registros.append({
            "identifier": header.findtext("oai:identifier", namespaces=namespaces),
            "datestamp": formatear_fecha(header.findtext("oai:datestamp", namespaces=namespaces)),
            "set_spec": header.findtext("oai:setSpec", namespaces=namespaces),
            "title_es": metadata.findtext("dc:title[@xml:lang='es-ES']", namespaces=namespaces),
            "title_en": metadata.findtext("dc:title[@xml:lang='en-US']", namespaces=namespaces),
            "creator": metadata.findtext("dc:creator", namespaces=namespaces),
            "publisher": metadata.findtext("dc:publisher", namespaces=namespaces),
            "type": metadata.findtext("dc:type", namespaces=namespaces),
            "format": metadata.findtext("dc:format", namespaces=namespaces),
            "identifier_url": metadata.findtext("dc:identifier", namespaces=namespaces),
            "language": metadata.findtext("dc:language", namespaces=namespaces),
            "relation": metadata.findtext("dc:relation", namespaces=namespaces),
            "coverage": metadata.findtext("dc:coverage", namespaces=namespaces),
            "rights": metadata.findtext("dc:rights", namespaces=namespaces),
            "date": formatear_fecha(metadata.findtext("dc:date", namespaces=namespaces)),
            "subjects_es": [s.text for s in metadata.findall("dc:subject[@xml:lang='es-ES']", namespaces) if s.text],
            "subjects_en": [s.text for s in metadata.findall("dc:subject[@xml:lang='en-US']", namespaces) if s.text],
            "descriptions_es": [d.text for d in metadata.findall("dc:description[@xml:lang='es-ES']", namespaces) if d.text],
            "descriptions_en": [d.text for d in metadata.findall("dc:description[@xml:lang='en-US']", namespaces) if d.text],
            "sources": [src.text for src in metadata.findall("dc:source", namespaces) if src.text],
        })

    next_token = root.findtext("oai:ListRecords/oai:resumptionToken", namespaces=namespaces)
    return registros, next_token.strip() if next_token else None
