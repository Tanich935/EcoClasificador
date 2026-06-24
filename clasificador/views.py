from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.conf import settings
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
import uuid
import os

from ChatConIA import Procesador
from .models import RegistroResiduo

procesador = Procesador()
procesador.darApiKey("")

def home(request):
    registros = RegistroResiduo.objects.all().order_by('-fecha')[:6]  # últimos 6
    return render(request, 'clasificador/home.html', {'registros': registros})


def clasificar_imagen(request):
    if request.method == 'POST' and request.FILES.get('imagen'):
        try:
            archivo = request.FILES['imagen']
            ext = archivo.name.split('.')[-1].lower()
            nombre = f"captura_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"

            ruta_relativa = os.path.join('clasificaciones', nombre)
            default_storage.save(ruta_relativa, archivo)
            ruta_absoluta = os.path.join(settings.MEDIA_ROOT, ruta_relativa)

            objeto, categoria = procesador.clasificarImagen(ruta_absoluta)

            if objeto == "Error":
                return redirect('/?error=Error al clasificar')

            registro = RegistroResiduo.objects.create(
                objeto=objeto,
                categoria=categoria,
                imagen=ruta_relativa
            )

            if categoria == "RECICLABLE":
                return redirect('contabilidad', registro_id=registro.id)
            else:
                return redirect('resultado')

        except Exception as e:
            return redirect(f'/?error=Error: {str(e)}')

    return redirect('home')



def resultado(request):
    ultimo = RegistroResiduo.objects.order_by('-fecha').first()
    if not ultimo:
        return redirect('home')
    
    return render(request, 'clasificador/resultado.html', {'registro': ultimo})
