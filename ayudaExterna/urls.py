from django.urls import path
from . import views

urlpatterns = [
    path('', views.panel_principal, name='panel_accesibilidad'),
    path('guardar-captura/', views.guardar_captura, name='guardar_captura'),
]