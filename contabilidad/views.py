from clasificador.models import RegistroResiduo
from .models import MovimientoFinanciero
from django.shortcuts import render, redirect, get_object_or_404


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

