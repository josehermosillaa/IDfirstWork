from config import settings
from django.db import models

# Create your models here.

class Cementera(models.Model):
    """filtrado por created, ya que los datos son mensuales"""
    nombre = models.CharField(max_length=255,verbose_name='Nombre producto generico')
    linea= models.DecimalField(max_digits=19,decimal_places=4, verbose_name='Suma de MontoLineaAdjudicada')
    cantidad = models.DecimalField(max_digits=19,decimal_places=4,verbose_name='Suma de CantidadAdjudicada')
    cuenta = models.IntegerField(verbose_name='Cuenta de MontoLineaAdjudicada')
    codigo_fecha = models.CharField(max_length=6,verbose_name='mes-año')

    created = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated = models.DateTimeField(auto_now=True, verbose_name='Fecha de actuialización')
    
    class Meta:
        unique_together = ('nombre', 'codigo_fecha')

    def __str__(self):
        return self.codigo_fecha +'/' +self.nombre
