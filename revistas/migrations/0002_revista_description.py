# Generated by Django 5.1.3 on 2024-12-20 07:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('revistas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='revista',
            name='description',
            field=models.TextField(blank=True, null=True, verbose_name='Descripción'),
        ),
    ]
