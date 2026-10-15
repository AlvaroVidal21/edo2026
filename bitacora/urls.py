from django.urls import path

from . import views

app_name = "bitacora"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("directorio/", views.directorio, name="directorio"),
    path("empresas/nueva/", views.empresa_nueva, name="empresa_nueva"),
    path("empresas/<int:pk>/", views.empresa_detalle, name="empresa_detalle"),
    path("empresas/<int:pk>/editar/", views.empresa_editar, name="empresa_editar"),
    path("actividades/", views.actividades, name="actividades"),
    path("actividades/nueva/", views.actividad_nueva, name="actividad_nueva"),
    path("critica/", views.criticas, name="criticas"),
    path("critica/nueva/", views.critica_nueva, name="critica_nueva"),
]
