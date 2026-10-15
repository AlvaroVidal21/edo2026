from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from .models import Actividad, CategoriaActividad, Critica, Empresa, Medio


@admin.register(Empresa)
class EmpresaAdmin(SimpleHistoryAdmin):
    list_display = ("ruc", "razon_social", "situacion_empresa", "estado_encuesta", "estado_critica")
    list_filter = ("situacion_empresa", "estado_encuesta", "estado_critica")
    search_fields = ("ruc", "razon_social", "contacto_principal_nombre")


@admin.register(Actividad)
class ActividadAdmin(admin.ModelAdmin):
    list_display = ("fecha", "empresa", "medio", "categoria")
    list_filter = ("medio", "categoria", "fecha")
    search_fields = ("empresa__ruc", "empresa__razon_social", "descripcion")


@admin.register(Critica)
class CriticaAdmin(SimpleHistoryAdmin):
    list_display = ("empresa", "variable_analizada", "tipo_resultado", "estado_revision", "creado_en")
    list_filter = ("tipo_resultado", "nivel_confianza", "estado_revision")
    search_fields = ("empresa__ruc", "empresa__razon_social", "variable_analizada")


@admin.register(Medio)
class MedioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    list_filter = ("activo",)


@admin.register(CategoriaActividad)
class CategoriaActividadAdmin(admin.ModelAdmin):
    list_display = ("nombre", "activo")
    list_filter = ("activo",)
