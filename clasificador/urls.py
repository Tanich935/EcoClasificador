from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('clasificar/', views.clasificar_imagen, name='clasificar_imagen'),
    path('resultado/', views.resultado, name='resultado'),
    
    path('contabilidad/<int:registro_id>/', views.contabilidad, name='contabilidad'),
    path('calcular-botella/<int:registro_id>/', views.calcular_botella, name='calcular_botella'),
    path('calcular-papel/<int:registro_id>/', views.calcular_papel, name='calcular_papel'),
    path('contabilidad/', views.contabilidad_dashboard, name='contabilidad_dashboard'),
    path('registrar-egreso/', views.registrar_egreso, name='registrar_egreso'),
    path('logros/', views.logros, name='logros'),
]