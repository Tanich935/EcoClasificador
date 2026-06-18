from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import base64
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage

def panel_principal(request):
    return render(request, 'ayudaExterna/panel.html')

@csrf_exempt
def guardar_captura(request):
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            image_data = data.get('imagen')
            
            format, imgstr = image_data.split(';base64,') 
            ext = format.split('/')[-1] 
            
            archivo_imagen = ContentFile(base64.b64decode(imgstr))
            default_storage.save(f"captura_accesibilidad.{ext}", archivo_imagen)
            
            return JsonResponse({'status': 'ok', 'mensaje': 'Guardado'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'mensaje': str(e)}, status=400)
            
    return JsonResponse({'status': 'error', 'mensaje': 'Método no permitido'}, status=405)