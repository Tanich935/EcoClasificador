from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.panel_principal, name='panel_admin'),
    path('guardar-parametros/', views.guardar_parametros, name='guardar_parametros'),
    path('toggle-usuario/<int:user_id>/', views.toggle_usuario, name='toggle_usuario'),
    path('crear-operario/', views.crear_operario, name='crear_operario'),
    
    # Login y Logout personalizados
    path('login/', auth_views.LoginView.as_view(template_name='panelDeAdministracion/login.html'), name='login_custom'),
    path('logout/', views.logout_view, name='logout_custom'),
]