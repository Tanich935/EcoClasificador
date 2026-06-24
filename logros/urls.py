from django.urls import path
from . import views

urlpatterns = [
    path('logros/', views.logros, name='logros'),
]