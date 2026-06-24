from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.conf import settings
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
import uuid
import os
from dotenv import load_dotenv

from ChatConIA import Procesador
from .models import RegistroResiduo

load_dotenv()
procesador = Procesador()
<<<<<<< HEAD
procesador.darApiKey("")
=======
apikey = os.getenv("GEMINI_API_KEY")



if apikey:
    procesador.darApiKey(apikey)
else:
    print("ALERTA: No se encontró la API Key en el archivo .env")
>>>>>>> 23211a061f94cff7bd2cf23fdab18a731f636042

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



<<<<<<< HEAD
=======
def contabilidad(request, registro_id):
    registro = get_object_or_404(RegistroResiduo, id=registro_id)
    
    objeto_lower = registro.objeto.lower()
    es_papel = any(word in objeto_lower for word in ['papel', 'hoja', 'periódico', 'cartón', 'caja'])
    es_botella = any(word in objeto_lower for word in ['botella', 'botellas', 'plástico', 'pet', 'soda', 'envase'])

    cantidad_detectada = 1

    # 2. USAMOS TU LIBRERÍA OFICIAL PARA CONTAR OBJETOS
    if es_botella:
        ruta_absoluta = os.path.join(settings.MEDIA_ROOT, registro.imagen.name)
        cantidad_detectada = procesador.contarObjetos(ruta_absoluta, "botellas, envases plásticos o PET")

    return render(request, 'clasificador/contabilidad.html', {
        'registro': registro,
        'es_papel': es_papel,
        'es_botella': es_botella,
        'cantidad_detectada': cantidad_detectada,
    })

# ====================== CONTABILIDAD ======================

def calcular_botella(request, registro_id):
    registro = get_object_or_404(RegistroResiduo, id=registro_id)
    
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
            peso_por_botella = 0.025
            precio_por_kg = 1.50

            peso_total = cantidad * peso_por_botella
            ganancia = peso_total * precio_por_kg

            # === REGISTRAR INGRESO EN CONTABILIDAD ===
            from .models import MovimientoFinanciero
            MovimientoFinanciero.objects.create(
                tipo='INGRESO',
                descripcion=f"Venta de {cantidad} {registro.objeto}",
                monto=round(ganancia, 2),
                registro_residuo=registro
            )

            return render(request, 'clasificador/resultado_contabilidad.html', {
                'registro': registro,
                'tipo': 'botella',
                'cantidad': cantidad,
                'peso_total': round(peso_total, 3),
                'ganancia': round(ganancia, 2),
            })
        except:
            pass

    return redirect('contabilidad', registro_id=registro_id)


def calcular_papel(request, registro_id):
    registro = get_object_or_404(RegistroResiduo, id=registro_id)
    
    if request.method == 'POST' and request.FILES.get('imagen_secundaria'):
        # Simulación por ahora (después mejoramos con IA)
        cantidad_hojas = 50  
        peso_total = cantidad_hojas * 0.005  
        precio_por_kg = 1.20
        ganancia = peso_total * precio_por_kg

        # === REGISTRAR INGRESO EN CONTABILIDAD ===
        from .models import MovimientoFinanciero
        MovimientoFinanciero.objects.create(
            tipo='INGRESO',
            descripcion=f"Venta de papel - {registro.objeto}",
            monto=round(ganancia, 2),
            registro_residuo=registro
        )

        return render(request, 'clasificador/resultado_contabilidad.html', {
            'registro': registro,
            'tipo': 'papel',
            'peso_total': round(peso_total, 3),
            'ganancia': round(ganancia, 2),
            'nota': 'Análisis con moneda pendiente'
        })

    return redirect('contabilidad', registro_id=registro_id)


>>>>>>> 23211a061f94cff7bd2cf23fdab18a731f636042
def resultado(request):
    ultimo = RegistroResiduo.objects.order_by('-fecha').first()
    if not ultimo:
        return redirect('home')
    
    return render(request, 'clasificador/resultado.html', {'registro': ultimo})
