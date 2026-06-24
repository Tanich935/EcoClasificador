
from django.urls import path
from .views import dashboard_reportes

urlpatterns = [
    path('reportes/', dashboard_reportes, name='reportes'),
]
