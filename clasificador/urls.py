from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('clasificar/', views.clasificar_imagen, name='clasificar_imagen'),
    path('resultado/', views.resultado, name='resultado'),
]