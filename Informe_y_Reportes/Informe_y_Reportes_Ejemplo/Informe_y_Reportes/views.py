from django.shortcuts import render
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from clasificador.models import RegistroResiduo, MovimientoFinanciero

def dashboard_reportes(request):
    categorias = RegistroResiduo.objects.values(
        'categoria'
    ).annotate(total=Count('id'))

    mensual = RegistroResiduo.objects.annotate(
        mes=TruncMonth('fecha')
    ).values('mes').annotate(
        total=Count('id')
    ).order_by('mes')

    top_objetos = RegistroResiduo.objects.values(
        'objeto'
    ).annotate(total=Count('id')).order_by('-total')[:10]

    ingresos = MovimientoFinanciero.objects.filter(
        tipo='INGRESO'
    ).aggregate(total=Sum('monto'))['total'] or 0

    egresos = MovimientoFinanciero.objects.filter(
        tipo='EGRESO'
    ).aggregate(total=Sum('monto'))['total'] or 0

    return render(request,'reportes.html',{
        'categorias': categorias,
        'mensual': mensual,
        'top_objetos': top_objetos,
        'ingresos': ingresos,
        'egresos': egresos,
        'ganancia_neta': ingresos-egresos
    })
