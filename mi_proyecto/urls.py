from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('clasificador.urls')),
    path('', include('contabilidad.urls')),
    path('', include('logros.urls')),
    path('ayuda-externa/', include('ayudaExterna.urls')),
    path('panel/', include('panelDeAdministracion.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)