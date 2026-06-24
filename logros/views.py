from django.shortcuts import render, redirect
from .models import RegistroResiduo

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