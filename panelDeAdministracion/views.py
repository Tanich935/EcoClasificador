from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from clasificador.models import RegistroResiduo
from .models import ParametroGlobal
from django.contrib.auth import logout

# === NUEVA FUNCIÓN DE CIERRE DE SESIÓN ===
def logout_view(request):
    logout(request)
    return redirect('/') 

def es_administrador(user):
    return user.is_authenticated and user.is_staff

@user_passes_test(es_administrador, login_url='/panel/login/')
def panel_principal(request):
    ParametroGlobal.objects.get_or_create(nombre='PRECIO_KG_RECICLABLE', defaults={'valor': 2.50, 'descripcion': 'Precio por Kg de material reciclable (Bs)'})
    ParametroGlobal.objects.get_or_create(nombre='LIMITE_CAPACIDAD', defaults={'valor': 1000.0, 'descripcion': 'Límite de capacidad del almacén (Kg)'})

    parametros = ParametroGlobal.objects.all()
    usuarios = User.objects.all().order_by('-date_joined')
    
    total_escaneos = RegistroResiduo.objects.count()
    reciclables = RegistroResiduo.objects.filter(categoria='RECICLABLE').count()
    no_reciclables = RegistroResiduo.objects.filter(categoria='NO_RECICLABLE').count()
    aprovechables = RegistroResiduo.objects.filter(categoria='APROVECHABLE').count()
    infecciosos = RegistroResiduo.objects.filter(categoria='INFECCIOSO').count()
    ultimos_registros = RegistroResiduo.objects.all().order_by('-fecha')[:10]

    context = {
        'total_escaneos': total_escaneos,
        'total_usuarios': usuarios.count(),
        'reciclables': reciclables, 'no_reciclables': no_reciclables,
        'aprovechables': aprovechables, 'infecciosos': infecciosos,
        'ultimos_registros': ultimos_registros,
        'parametros': parametros,
        'usuarios': usuarios,
    }
    return render(request, 'panelDeAdministracion/panel.html', context)

@user_passes_test(es_administrador, login_url='/panel/login/')
def guardar_parametros(request):
    if request.method == 'POST':
        for param in ParametroGlobal.objects.all():
            nuevo_valor = request.POST.get(param.nombre)
            if nuevo_valor:
                param.valor = float(nuevo_valor)
                param.save()
    return redirect('panel_admin')

@user_passes_test(es_administrador, login_url='/panel/login/')
def toggle_usuario(request, user_id):
    usuario = get_object_or_404(User, id=user_id)
    if not usuario.is_superuser:
        usuario.is_active = not usuario.is_active
        usuario.save()
    return redirect('panel_admin')

@user_passes_test(es_administrador, login_url='/panel/login/')
def crear_operario(request):
    if request.method == 'POST':
        nombre_usuario = request.POST.get('username')
        contrasena = request.POST.get('password')
        es_admin = request.POST.get('is_admin') == 'on'
        
        if nombre_usuario and contrasena:
            if not User.objects.filter(username=nombre_usuario).exists():
                user = User.objects.create_user(username=nombre_usuario, password=contrasena)
                if es_admin:
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
    return redirect('panel_admin')