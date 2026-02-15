# apps/administracion/models/agregado_precio.py
from django.db import models
from datetime import date
from django.db.models import Max
from apps.administracion.models.agregado import Agregado

from utils.mixins.codigo_mixin import GeneradorCodigoConfigurableMixin
from utils.mixins.atributos_fechas_mixin import AtributosFechasMixin
from simple_history.models              import HistoricalRecords

class AgregadoPrecio(
        GeneradorCodigoConfigurableMixin,
        AtributosFechasMixin,
        models.Model
    ):
    
    CODIGO_PREFIJO = 'CA'
    CODIGO_MINIMO = 1000
    
    agregado = models.ForeignKey(Agregado, on_delete=models.PROTECT, related_name='precios')
    codigo = models.CharField('Código', max_length=20, unique=True)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    motivo_cambio = models.CharField('Motivo Cambio', max_length=255, blank=True)
    is_active = models.BooleanField('Activo', default=True)
    historical = HistoricalRecords()

    class Meta:
        managed = True
        # db_table = 'agregado_precio'
        db_table = 'administracion\".\"agregado_precio'
        verbose_name = 'Precio de Agregado'
        verbose_name_plural = 'Precios de Agregados'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.agregado.nombre}: ${self.precio}'

    def save(self, *args, **kwargs):
        # Si es nuevo y activo, desactivar el anterior
        if not self.pk and self.is_active:
            anteriores = AgregadoPrecio.objects.filter(
                agregado=self.agregado,
                is_active=True
            )
            for anterior in anteriores:
                anterior.is_active = False
                anterior.fecha_fin = date.today()
                anterior.save()
        
        super().save(*args, **kwargs)