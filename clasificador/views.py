from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage
from django.conf import settings
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv
from django.contrib.auth.decorators import login_required

from panelDeAdministracion.models import ParametroGlobal
from ChatConIA import Procesador
from .models import RegistroResiduo

load_dotenv()
procesador = Procesador()
apikey = os.getenv("GEMINI_API_KEY")

if apikey:
    procesador.darApiKey(apikey)
else:
    print("ALERTA: No se encontró la API Key en el archivo .env")


@login_required(login_url='/panel/login/')
def home(request):
    registros = RegistroResiduo.objects.all().order_by('-fecha')[:6]  # últimos 6
    return render(request, 'clasificador/home.html', {'registros': registros})


@login_required(login_url='/panel/login/')
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


@login_required(login_url='/panel/login/')
def contabilidad(request, registro_id):
    registro = get_object_or_404(RegistroResiduo, id=registro_id)
    
    objeto_lower = registro.objeto.lower()
    es_papel = any(word in objeto_lower for word in ['papel', 'hoja', 'periódico', 'cartón', 'caja'])
    es_botella = any(word in objeto_lower for word in ['botella', 'botellas', 'plástico', 'pet', 'soda', 'envase'])

    cantidad_detectada = 1

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

@login_required(login_url='/panel/login/')
def calcular_botella(request, registro_id):
    registro = get_object_or_404(RegistroResiduo, id=registro_id)
    
    if request.method == 'POST':
        try:
            cantidad = int(request.POST.get('cantidad', 1))
            peso_por_botella = 0.025
            
            try:
                parametro = ParametroGlobal.objects.get(nombre='PRECIO_KG_RECICLABLE')
                precio_por_kg = parametro.valor
            except ParametroGlobal.DoesNotExist:
                precio_por_kg = 1.50

            peso_total = cantidad * peso_por_botella
            ganancia = peso_total * precio_por_kg

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


@login_required(login_url='/panel/login/')
def calcular_papel(request, registro_id):
    registro = get_object_or_404(RegistroResiduo, id=registro_id)
    
    if request.method == 'POST' and request.FILES.get('imagen_secundaria'):
        cantidad_hojas = 50  
        peso_total = cantidad_hojas * 0.005  
        
        try:
            parametro = ParametroGlobal.objects.get(nombre='PRECIO_KG_PAPEL')
            precio_por_kg = parametro.valor
        except ParametroGlobal.DoesNotExist:
            precio_por_kg = 1.20 
        
        ganancia = peso_total * precio_por_kg

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


@login_required(login_url='/panel/login/')
def resultado(request):
    ultimo = RegistroResiduo.objects.order_by('-fecha').first()
    if not ultimo:
        return redirect('home')
    
    return render(request, 'clasificador/resultado.html', {'registro': ultimo})


# ====================== CONTABILIDAD (Ingresos y Egresos) ======================

@login_required(login_url='/panel/login/')
def contabilidad_dashboard(request):
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


@login_required(login_url='/panel/login/')
def registrar_egreso(request):
    from .models import MovimientoFinanciero
    
    if request.method == 'POST':
        MovimientoFinanciero.objects.create(
            tipo='EGRESO',
            descripcion=request.POST.get('descripcion', 'Egreso sin descripción'),
            monto=float(request.POST.get('monto', 0))
        )
        return redirect('contabilidad_dashboard')
    
    return render(request, 'clasificador/registrar_egreso.html')


@login_required(login_url='/panel/login/')
def logros(request):
    total = RegistroResiduo.objects.count()

    logros = [
        {"nombre": "🌱 Eco Novato", "meta": 25, "cumplido": total >= 25},
        {"nombre": "♻️ Eco Protector", "meta": 100, "cumplido": total >= 100},
        {"nombre": "🏆 Eco Maestro", "meta": 250, "cumplido": total >= 250}
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