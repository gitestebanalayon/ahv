# apps/administracion/models/precio_rango_pedido.py
from django.db import models
from datetime import date
from django.db.models import Max
from apps.administracion.models.hult_delivery import HultDelivery


class PrecioHultDelivery(models.Model):
    hult_delivery = models.ForeignKey(HultDelivery, on_delete=models.PROTECT, related_name='precios')
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField('Fecha Inicio', default=date.today)
    fecha_fin = models.DateField('Fecha Fin', null=True, blank=True)
    motivo_cambio = models.CharField('Motivo Cambio', max_length=255, blank=True)
    is_active = models.BooleanField('Activo', default=False)
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha Actualización', auto_now=True)

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
        # Si es nuevo y no tiene fecha_inicio, usar hoy
        # if not self.pk and not self.fecha_inicio:
        #     self.fecha_inicio = timezone.now().date()
        
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