# apps/administracion/models/precio_rango_pedido.py
from django.db import models
from datetime import date
from django.db.models import Max
from apps.administracion.models.hult_delivery import HultDelivery

from utils.mixins.codigo_mixin import GeneradorCodigoConfigurableMixin
from utils.mixins.atributos_fechas_mixin import AtributosFechasMixin
from simple_history.models import HistoricalRecords

class PrecioHultDelivery(
        GeneradorCodigoConfigurableMixin,
        AtributosFechasMixin,
        models.Model
    ):
    
    CODIGO_PREFIJO = 'CM'
    CODIGO_MINIMO = 1000
    
    hult_delivery = models.ForeignKey(HultDelivery, on_delete=models.PROTECT, related_name='precios')
    codigo = models.CharField('Código', max_length=20, unique=True)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    motivo_cambio = models.CharField('Motivo Cambio', max_length=255, blank=True)
    is_active = models.BooleanField('Activo', default=True)
    historical = HistoricalRecords()
   
    class Meta:
        managed = True
        # db_table = 'precio_rango_pedido'
        db_table = 'administracion\".\"precio_hult_delivery'
        verbose_name = 'Precio por Hult Delivery'
        verbose_name_plural = 'Precios por Hult Delivery'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.hult_delivery.nombre}: ${self.precio}'

    def save(self, *args, **kwargs):
        
        # Si es nuevo y activo, desactivar el anterior
        if not self.pk:
            anteriores = PrecioHultDelivery.objects.filter(
                hult_delivery=self.hult_delivery,
                fecha_fin__isnull=True,
                is_active=True
            )
            for anterior in anteriores:
                anterior.is_active = False
                anterior.fecha_fin = date.today()
                anterior.save()
        
        super().save(*args, **kwargs)