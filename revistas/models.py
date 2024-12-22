from django.db import models
import requests
from xml.etree import ElementTree as ET
from django.utils.timezone import now
from datetime import datetime

class Revista(models.Model):
    # Campos esenciales
    cover_image = models.ImageField(upload_to='revistas/covers/', null=True, blank=True, verbose_name="Imagen de Portada")
    repository_name = models.CharField(max_length=255, verbose_name="Nombre del Repositorio", unique=True)
    base_url = models.URLField(verbose_name="URL Base", unique=True)
    protocol_version = models.CharField(max_length=50, verbose_name="Versión del Protocolo")
    admin_email = models.EmailField(verbose_name="Email del Administrador")
    earliest_datestamp = models.DateTimeField(verbose_name="Fecha del Registro Más Antiguo")
    deleted_record_policy = models.CharField(max_length=50, verbose_name="Política de Registros Eliminados")
    granularity = models.CharField(max_length=50, verbose_name="Granularidad de Fechas")

    # Opcionales y adicionales
    compressions = models.TextField(blank=True, null=True, verbose_name="Métodos de Compresión Soportados")
    repository_identifier = models.CharField(max_length=255, blank=True, null=True, verbose_name="Identificador del Repositorio")
    delimiter = models.CharField(max_length=5, blank=True, null=True, verbose_name="Delimitador")
    sample_identifier = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ejemplo de Identificador")
    toolkit_title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Título del Toolkit")
    toolkit_author_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Autor del Toolkit")
    toolkit_author_email = models.EmailField(blank=True, null=True, verbose_name="Email del Autor del Toolkit")
    toolkit_version = models.CharField(max_length=50, blank=True, null=True, verbose_name="Versión del Toolkit")
    toolkit_url = models.URLField(blank=True, null=True, verbose_name="URL del Toolkit")
    official_url = models.URLField(max_length=255, blank=True, null=True, verbose_name="URL Oficial")
    publisher = models.CharField(max_length=255, blank=True, null=True, verbose_name="Editorial")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")
    metadata_prefix = models.CharField(max_length=50, default="oai_dc", verbose_name="Prefijo de Metadatos")



    # Campos adicionales para la gestión
    last_harvest_date = models.DateTimeField(blank=True, null=True, verbose_name="Última Fecha de Cosecha")

    class Meta:
        verbose_name = "Revista"
        verbose_name_plural = "Revistas"

    def __str__(self):
        return self.repository_name or "Revista sin nombre"


    def fetch_sets(self):
        """
        Obtiene los conjuntos disponibles del repositorio mediante el verbo ListSets.
        """
        try:
            response = requests.get(f"{self.base_url}?verb=ListSets")
            response.raise_for_status()

            namespaces = {"oai": "http://www.openarchives.org/OAI/2.0/"}
            root = ET.fromstring(response.text)

            sets = []
            for set_element in root.findall(".//oai:set", namespaces):
                set_name = set_element.find(".//oai:setSpec", namespaces).text
                sets.append(set_name)

            self.sets = "; ".join(sets)  # Almacena los conjuntos separados por ";"
        except Exception as e:
            raise ValueError(f"Error al obtener conjuntos de {self.base_url}: {e}")


    def fetch_metadata(self):
        """
        Extrae metadatos de la URL OAI-PMH y asigna los campos relevantes.
        """
        try:
            response = requests.get(f"{self.base_url}?verb=Identify")
            response.raise_for_status()

            namespaces = {
                "oai": "http://www.openarchives.org/OAI/2.0/",
                "oai-identifier": "http://www.openarchives.org/OAI/2.0/oai-identifier",
                "toolkit": "http://oai.dlib.vt.edu/OAI/metadata/toolkit",
            }
            root = ET.fromstring(response.text)

                # Asignación de campos devueltos por Identify
            self.repository_name = root.find(".//oai:repositoryName", namespaces).text
            self.protocol_version = root.find(".//oai:protocolVersion", namespaces).text
            # Manejo de fechas con o sin 'Z'
            fecha = root.find(".//oai:earliestDatestamp", namespaces).text
            try:
                self.earliest_datestamp = datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                self.earliest_datestamp = datetime.strptime(fecha, "%Y-%m-%dT%H:%M:%S")

            self.deleted_record_policy = root.find(".//oai:deletedRecord", namespaces).text
            self.granularity = root.find(".//oai:granularity", namespaces).text
            self.admin_email = root.find(".//oai:adminEmail", namespaces).text

                # Opcionales: compresiones
            compression_elements = root.findall(".//oai:compression", namespaces)
            self.compressions = "; ".join([el.text for el in compression_elements if el.text])

                # Descripciones
            for description in root.findall(".//oai:description", namespaces):
                # Identificador del Repositorio
                if description.find(".//oai-identifier:repositoryIdentifier", namespaces):
                    self.repository_identifier = description.find(
                        ".//oai-identifier:repositoryIdentifier", namespaces
                    ).text
                    self.delimiter = description.find(".//oai-identifier:delimiter", namespaces).text
                    self.sample_identifier = description.find(
                        ".//oai-identifier:sampleIdentifier", namespaces
                    ).text

                    # Toolkit
                    if description.find(".//toolkit:title", namespaces):
                        self.toolkit_title = description.find(".//toolkit:title", namespaces).text
                    self.toolkit_author_name = description.find(".//toolkit:author/toolkit:name", namespaces).text
                    self.toolkit_author_email = description.find(".//toolkit:author/toolkit:email", namespaces).text
                    self.toolkit_version = description.find(".//toolkit:version", namespaces).text
                    self.toolkit_url = description.find(".//toolkit:URL", namespaces).text

                # Formatear la URL oficial
                self.format_official_url()

        except Exception as e:
            raise ValueError(f"Error al extraer los datos de {self.base_url}: {e}")

    
    def format_official_url(self):
        """
        Formatea la base_url para obtener la official_url eliminando el sufijo '/oai'.
        """
        if self.base_url.endswith('/oai'):
            self.official_url = self.base_url[:-4]
        else:
            self.official_url = self.base_url

    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para extraer automáticamente los metadatos
        si la revista no tiene nombre y formatear la URL oficial.
        """
        if not self.official_url:
            self.format_official_url()
        if not self.repository_name:
            self.fetch_metadata()
        super().save(*args, **kwargs)

class Articulo(models.Model):
    fuente = models.ForeignKey(
        "Revista", on_delete=models.CASCADE, related_name="articulos", verbose_name="Fuente"
    )
    identifier = models.CharField(max_length=255, verbose_name="Identificador OAI", unique=True)
    datestamp = models.DateTimeField(blank=True, null=True, verbose_name="Fecha de Modificación del Registro")
    set_spec = models.CharField(max_length=255, blank=True, null=True, verbose_name="Conjunto Específico (SetSpec)")

    # Dublin Core Fields
    title_es = models.TextField(blank=True, null=True, verbose_name="Título en Español")
    title_en = models.TextField(blank=True, null=True, verbose_name="Título en Inglés")
    creator = models.CharField(max_length=255, blank=True, null=True, verbose_name="Creador")
    publisher = models.CharField(max_length=255, blank=True, null=True, verbose_name="Editor")
    type = models.CharField(max_length=255, blank=True, null=True, verbose_name="Tipo")
    format = models.CharField(max_length=255, blank=True, null=True, verbose_name="Formato")
    identifier_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="Identificador URL")
    language = models.CharField(max_length=50, blank=True, null=True, verbose_name="Idioma")
    relation = models.TextField(blank=True, null=True, verbose_name="Relación")
    coverage = models.TextField(blank=True, null=True, verbose_name="Cobertura")
    rights = models.TextField(blank=True, null=True, verbose_name="Derechos")
    date = models.DateField(blank=True, null=True, verbose_name="Fecha de Publicación")

    # Multivalores y Relaciones
    subjects_es = models.TextField(blank=True, null=True, verbose_name="Temas en Español (Concatenados)")
    subjects_en = models.TextField(blank=True, null=True, verbose_name="Temas en Inglés (Concatenados)")
    descriptions_es = models.TextField(blank=True, null=True, verbose_name="Descripciones en Español (Concatenadas)")
    descriptions_en = models.TextField(blank=True, null=True, verbose_name="Descripciones en Inglés (Concatenadas)")
    sources = models.TextField(blank=True, null=True, verbose_name="Fuentes (Concatenadas)")

    class Meta:
        verbose_name = "Artículo"
        verbose_name_plural = "Artículos"

    def __str__(self):
        return self.title_es or self.title_en or "Artículo sin título"

