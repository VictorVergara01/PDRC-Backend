# Generated by Django 5.1.3 on 2024-12-20 06:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Revista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='revistas/covers/', verbose_name='Imagen de Portada')),
                ('repository_name', models.CharField(max_length=255, unique=True, verbose_name='Nombre del Repositorio')),
                ('base_url', models.URLField(unique=True, verbose_name='URL Base')),
                ('protocol_version', models.CharField(max_length=50, verbose_name='Versión del Protocolo')),
                ('admin_email', models.EmailField(max_length=254, verbose_name='Email del Administrador')),
                ('earliest_datestamp', models.DateTimeField(verbose_name='Fecha del Registro Más Antiguo')),
                ('deleted_record_policy', models.CharField(max_length=50, verbose_name='Política de Registros Eliminados')),
                ('granularity', models.CharField(max_length=50, verbose_name='Granularidad de Fechas')),
                ('compressions', models.TextField(blank=True, null=True, verbose_name='Métodos de Compresión Soportados')),
                ('repository_identifier', models.CharField(blank=True, max_length=255, null=True, verbose_name='Identificador del Repositorio')),
                ('delimiter', models.CharField(blank=True, max_length=5, null=True, verbose_name='Delimitador')),
                ('sample_identifier', models.CharField(blank=True, max_length=255, null=True, verbose_name='Ejemplo de Identificador')),
                ('toolkit_title', models.CharField(blank=True, max_length=255, null=True, verbose_name='Título del Toolkit')),
                ('toolkit_author_name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Autor del Toolkit')),
                ('toolkit_author_email', models.EmailField(blank=True, max_length=254, null=True, verbose_name='Email del Autor del Toolkit')),
                ('toolkit_version', models.CharField(blank=True, max_length=50, null=True, verbose_name='Versión del Toolkit')),
                ('toolkit_url', models.URLField(blank=True, null=True, verbose_name='URL del Toolkit')),
                ('official_url', models.URLField(blank=True, max_length=255, null=True, verbose_name='URL Oficial')),
                ('publisher', models.CharField(blank=True, max_length=255, null=True, verbose_name='Editorial')),
                ('last_harvest_date', models.DateTimeField(blank=True, null=True, verbose_name='Última Fecha de Cosecha')),
            ],
            options={
                'verbose_name': 'Revista',
                'verbose_name_plural': 'Revistas',
            },
        ),
        migrations.CreateModel(
            name='Articulo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('identifier', models.CharField(max_length=255, unique=True, verbose_name='Identificador OAI')),
                ('datestamp', models.DateTimeField(blank=True, null=True, verbose_name='Fecha de Modificación del Registro')),
                ('set_spec', models.CharField(blank=True, max_length=255, null=True, verbose_name='Conjunto Específico (SetSpec)')),
                ('title_es', models.TextField(blank=True, null=True, verbose_name='Título en Español')),
                ('title_en', models.TextField(blank=True, null=True, verbose_name='Título en Inglés')),
                ('creator', models.CharField(blank=True, max_length=255, null=True, verbose_name='Creador')),
                ('publisher', models.CharField(blank=True, max_length=255, null=True, verbose_name='Editor')),
                ('type', models.CharField(blank=True, max_length=255, null=True, verbose_name='Tipo')),
                ('format', models.CharField(blank=True, max_length=255, null=True, verbose_name='Formato')),
                ('identifier_url', models.URLField(blank=True, max_length=500, null=True, verbose_name='Identificador URL')),
                ('language', models.CharField(blank=True, max_length=50, null=True, verbose_name='Idioma')),
                ('relation', models.TextField(blank=True, null=True, verbose_name='Relación')),
                ('coverage', models.TextField(blank=True, null=True, verbose_name='Cobertura')),
                ('rights', models.TextField(blank=True, null=True, verbose_name='Derechos')),
                ('date', models.DateField(blank=True, null=True, verbose_name='Fecha de Publicación')),
                ('subjects_es', models.TextField(blank=True, null=True, verbose_name='Temas en Español (Concatenados)')),
                ('subjects_en', models.TextField(blank=True, null=True, verbose_name='Temas en Inglés (Concatenados)')),
                ('descriptions_es', models.TextField(blank=True, null=True, verbose_name='Descripciones en Español (Concatenadas)')),
                ('descriptions_en', models.TextField(blank=True, null=True, verbose_name='Descripciones en Inglés (Concatenadas)')),
                ('sources', models.TextField(blank=True, null=True, verbose_name='Fuentes (Concatenadas)')),
                ('fuente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='articulos', to='revistas.revista', verbose_name='Fuente')),
            ],
            options={
                'verbose_name': 'Artículo',
                'verbose_name_plural': 'Artículos',
            },
        ),
    ]
