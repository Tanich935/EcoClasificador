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
procesador.darApiKey("AIzaSyB4R4YbYxsAm7e5x6xr_LKJiFrV6Empxsk")

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



def contabilidad(request, registro_id):
    registro = get_object_or_404(RegistroResiduo, id=registro_id)
    
    objeto_lower = registro.objeto.lower()
    es_papel = any(word in objeto_lower for word in ['papel', 'hoja', 'periódico', 'cartón', 'caja'])
    es_botella = any(word in objeto_lower for word in ['botella', 'botellas', 'plástico', 'pet', 'soda', 'envase'])

    cantidad_detectada = 1

    if es_botella:
        try:
            from PIL import Image
            import re
            
            ruta_absoluta = os.path.join(settings.MEDIA_ROOT, registro.imagen.name)
            imagen = Image.open(ruta_absoluta)
            
            prompt = """
            Cuenta cuántas botellas, envases plásticos o PET hay en esta imagen.
            Responde SOLO con un número entero. Si no ves botellas claras, responde 1.
            """
            
            respuesta = procesador.model.generate_content([prompt, imagen])
            texto = respuesta.text.strip()
            
            print(f"🔍 IA respondió: {texto}")  # ← Esto te ayudará a ver qué dice la IA
            
            numeros = re.findall(r'\d+', texto)
            if numeros:
                cantidad_detectada = int(numeros[0])
                if cantidad_detectada < 1:
                    cantidad_detectada = 1
                    
        except Exception as e:
            print(f"❌ Error contando botellas: {e}")

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


def resultado(request):
    ultimo = RegistroResiduo.objects.order_by('-fecha').first()
    if not ultimo:
        return redirect('home')
    
    return render(request, 'clasificador/resultado.html', {'registro': ultimo})


# ====================== CONTABILIDAD (Ingresos y Egresos) ======================

def contabilidad_dashboard(request):
    """Dashboard simple de Contabilidad"""
    from .models import MovimientoFinanciero
    
    ingresos = MovimientoFinanciero.objects.filter(tipo='INGRESO')
    egresos = MovimientoFinanciero.objects.filter(tipo='EGRESO')
    
    total_ingresos = sum(m.monto for m in ingresos)
    total_egresos = sum(m.monto for m in egresos)
    balance = total_ingresos - total_egresos

    return render(request, 'clasificador/contabilidad_dashboard.html', {
        'total_ingresos': round(total_ingresos, 2),
        'total_egresos': round(total_egresos, 2),
        'balance': round(balance, 2),
    })


def registrar_egreso(request):
    """Registrar egresos (costos)"""
    from .models import MovimientoFinanciero
    
    if request.method == 'POST':
        MovimientoFinanciero.objects.create(
            tipo='EGRESO',
            descripcion=request.POST.get('descripcion', 'Egreso sin descripción'),
            monto=float(request.POST.get('monto', 0))
        )
        return redirect('contabilidad_dashboard')
    
    return render(request, 'clasificador/registrar_egreso.html')

def logros(request):
    total = RegistroResiduo.objects.count()

    logros = [
        {
            "nombre": "🌱 Eco Novato",
            "meta": 25,
            "cumplido": total >= 25
        },
        {
            "nombre": "♻️ Eco Protector",
            "meta": 100,
            "cumplido": total >= 100
        },
        {
            "nombre": "🏆 Eco Maestro",
            "meta": 250,
            "cumplido": total >= 250
        }
    ]

    reciclables = RegistroResiduo.objects.filter(categoria='RECICLABLE').count()
    no_reciclables = RegistroResiduo.objects.filter(categoria='NO_RECICLABLE').count()
    aprovechables = RegistroResiduo.objects.filter(categoria='APROVECHABLE').count()
    infecciosos = RegistroResiduo.objects.filter(categoria='INFECCIOSO').count()

    return render(request, 'clasificador/logros.html', {
        'total': total,
        'logros': logros,
        'reciclables': reciclables,
        'no_reciclables': no_reciclables,
        'aprovechables': aprovechables,
        'infecciosos': infecciosos,
    })