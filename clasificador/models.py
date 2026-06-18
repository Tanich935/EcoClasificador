from django.db import models
from django.utils import timezone

class RegistroResiduo(models.Model):
    fecha = models.DateTimeField(default=timezone.now)
    objeto = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='clasificaciones/', null=True, blank=True)

    def __str__(self):
        return f"{self.objeto} - {self.categoria}"


class MovimientoFinanciero(models.Model):
    TIPO_CHOICES = [
        ('INGRESO', 'Ingreso - Venta de Reciclaje'),
        ('EGRESO', 'Egreso - Costo'),
    ]
    
    fecha = models.DateTimeField(default=timezone.now)
    tipo = models.CharField(max_length=10, choices=TIPO_CHOICES)
    descripcion = models.CharField(max_length=300)
    monto = models.DecimalField(max_digits=12, decimal_places=2)
    registro_residuo = models.ForeignKey(RegistroResiduo, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.descripcion} - Bs {self.monto}"