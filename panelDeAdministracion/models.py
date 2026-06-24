from django.db import models

class ParametroGlobal(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    valor = models.FloatField()
    descripcion = models.CharField(max_length=200)

    def __str__(self):
        return f"{self.nombre}: {self.valor}"