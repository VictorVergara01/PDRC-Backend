import csv
from django import forms
from django.http import HttpResponse
from django.contrib import admin, messages
from django.shortcuts import redirect, render
from django.urls import path, reverse
from django.utils.html import format_html
from import_export.admin import ImportExportMixin 
from .models import Revista, Articulo
from .resources import RevistaResource, ArticuloResource
from .utils import cosechar_datos_directo

@admin.register(Revista)
class RevistaAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = (
        'acciones',
        'cover_image_display',
        'repository_name',
        'description',
        'official_url',
        'base_url',
        'last_harvest_date',
        'publisher',
        'admin_email',
    )
    search_fields = ('repository_name', 'base_url', 'admin_email', 'official_url', 'description')
    list_filter = ('protocol_version', 'publisher',)
    resource_class = RevistaResource
    actions = ['cosecha_seleccionados']

    def cover_image_display(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit:cover;" />', obj.cover_image.url)
        return "No Image"
    cover_image_display.short_description = "Portada"

    def get_form(self, request, obj=None, **kwargs):
        if obj is None:
            kwargs['form'] = RevistaCreateForm
        return super().get_form(request, obj, **kwargs)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('cosechar/<int:pk>/', self.admin_site.admin_view(self.cosechar_revista), name='cosechar-revista'),
            path('<int:pk>/editar/', self.admin_site.admin_view(self.editar_revista), name='editar-revista'),
        ]
        return custom_urls + urls

    def cosechar_revista(self, request, pk):
        try:
            revista = Revista.objects.get(pk=pk)
            cosechar_datos_directo(revista.base_url, revista.metadata_prefix, revista.id)
            messages.success(request, f"Datos cosechados exitosamente desde la revista: {revista.repository_name}")
        except Exception as e:
            messages.error(request, f"Error al cosechar datos: {str(e)}")
        return redirect('admin:revistas_revista_changelist')

    def editar_revista(self, request, pk):
        revista = Revista.objects.get(pk=pk)
        if request.method == "POST":
            form = RevistaEditForm(request.POST, request.FILES, instance=revista)
            if form.is_valid():
                form.save()
                messages.success(request, "Revista editada exitosamente.")
                return redirect('admin:revistas_revista_changelist')
        else:
            form = RevistaEditForm(instance=revista)

        return render(
            request,
            "admin/editar_revista.html",
            {
                "form": form,
                "revista": revista,
                "opts": self.model._meta,
                "app_label": self.model._meta.app_label,
                "title": "Editar Revista",
            },
        )

    def acciones(self, obj):
        return format_html(
            '<a href="{}" class="button" style="margin-right: 10px;">Cosechar</a>'
            '<a href="{}" class="button">Editar</a>',
            reverse('admin:cosechar-revista', args=[obj.pk]),
            reverse('admin:editar-revista', args=[obj.pk]),
        )
    acciones.short_description = 'Acciones'
    
    def cosecha_seleccionados(self, request, queryset):
        """
        Realiza la cosecha de datos para las revistas seleccionadas.
        """
        if not queryset.exists():
            messages.error(request, "No se seleccionaron revistas para cosechar.")
            return
    
        errores = []
        exitos = 0
    
        for revista in queryset:
            try:
                # Reutilizamos la función `cosechar_datos_directo`
                cosechar_datos_directo(revista.base_url, revista.metadata_prefix, revista.id)
                exitos += 1
            except Exception as e:
                errores.append(f"Error al cosechar la revista '{revista.repository_name}': {str(e)}")
    
        # Mostrar mensajes en el admin
        if exitos:
            messages.success(request, f"Cosecha completada con éxito para {exitos} revista(s).")
        if errores:
            messages.error(request, "Ocurrieron errores:\n" + "\n".join(errores))
    
    cosecha_seleccionados.short_description = "Cosechar datos de las revistas seleccionadas"

@admin.register(Articulo)
class ArticuloAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ('title_es', 'title_en', 'publisher', 'language', 'rights')
    search_fields = ('title_es', 'title_en', 'publisher', 'language')
    list_filter = ('language',)
    ordering = ('-title_es',)
    resource_class = ArticuloResource


# Formulario personalizado para crear revistas
class RevistaCreateForm(forms.ModelForm):
    class Meta:
        model = Revista
        fields = ['base_url', 'description', 'cover_image']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.official_url:
            instance.official_url = instance.format_official_url()
        if commit:
            instance.save()
        return instance


class RevistaEditForm(forms.ModelForm):
    class Meta:
        model = Revista
        fields = ['repository_name', 'description', 'cover_image', 'base_url', 'official_url']

    def save(self, commit=True):
        instance = super().save(commit=False)
        if not instance.official_url:
            instance.official_url = instance.format_official_url()
        if commit:
            instance.save()
        return instance
