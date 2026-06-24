from django.db import models
from django.utils import timezone

class RegistroResiduo(models.Model):
    fecha = models.DateTimeField(default=timezone.now)
    objeto = models.CharField(max_length=200)
    categoria = models.CharField(max_length=50)
    imagen = models.ImageField(upload_to='clasificaciones/', null=True, blank=True)

    def __str__(self):
        return f"{self.objeto} - {self.categoria}"