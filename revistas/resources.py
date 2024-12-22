from import_export import resources, fields, widgets
from .models import Revista, Articulo

class RevistaResource(resources.ModelResource):
    class Meta:
        model = Revista
        fields = (
            'id',
            'repository_name',
            'description',
            'base_url',
            'protocol_version',
            'admin_email',
            'earliest_datestamp',
            'deleted_record_policy',
            'granularity',
            'compressions',
            'repository_identifier',
            'delimiter',
            'sample_identifier',
            'toolkit_title',
            'toolkit_author_name',
            'toolkit_author_email',
            'toolkit_version',
            'toolkit_url',
            'official_url',
            'publisher',
            'metadata_prefix',
            'last_harvest_date',
        )
        export_order = (
            'id',
            'repository_name',
            'description',
            'base_url',
            'protocol_version',
            'admin_email',
            'earliest_datestamp',
            'deleted_record_policy',
            'granularity',
            'compressions',
            'repository_identifier',
            'delimiter',
            'sample_identifier',
            'toolkit_title',
            'toolkit_author_name',
            'toolkit_author_email',
            'toolkit_version',
            'toolkit_url',
            'official_url',
            'publisher',
            'metadata_prefix',
            'last_harvest_date',
        )

class ArticuloResource(resources.ModelResource):
    fuente = fields.Field(
        attribute='fuente',
        column_name='Revista ID',
        widget=widgets.ForeignKeyWidget(Revista, 'id')  # Relación basada en el ID de la revista
    )

    def dehydrate_fuente(self, articulo):
        """
        Devuelve el ID de la revista relacionada o un mensaje si no hay fuente asignada.
        """
        if articulo.fuente:
            return articulo.fuente.id  # Devuelve el ID de la revista
        return "Sin fuente asignada"

    class Meta:
        model = Articulo
        fields = (
            'id',
            'fuente',  # Relación con Revista
            'identifier',
            'datestamp',
            'set_spec',
            'title_es',
            'title_en',
            'creator',
            'publisher',
            'type',
            'format',
            'identifier_url',
            'language',
            'relation',
            'coverage',
            'rights',
            'date',
            'subjects_es',
            'subjects_en',
            'descriptions_es',
            'descriptions_en',
            'sources',
        )
        export_order = (
            'id',
            'fuente',  # Relación con Revista
            'identifier',
            'datestamp',
            'set_spec',
            'title_es',
            'title_en',
            'creator',
            'publisher',
            'type',
            'format',
            'identifier_url',
            'language',
            'relation',
            'coverage',
            'rights',
            'date',
            'subjects_es',
            'subjects_en',
            'descriptions_es',
            'descriptions_en',
            'sources',
        )
