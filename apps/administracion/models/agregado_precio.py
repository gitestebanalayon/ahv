# apps/administracion/models/agregado_precio.py
from django.db import models
from django.utils import timezone
from apps.administracion.models.agregado import Agregado

class AgregadoPrecio(models.Model):
    agregado = models.ForeignKey(Agregado, on_delete=models.PROTECT, related_name='precios')
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField('Fecha Inicio', default=timezone.now)
    fecha_fin = models.DateField('Fecha Fin', null=True, blank=True)
    motivo_cambio = models.CharField('Motivo Cambio', max_length=255, blank=True)
    is_active = models.BooleanField('Activo', default=True)
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha Actualización', auto_now=True)

    class Meta:
        db_table = 'agregado_precio'
        verbose_name = 'Precio de Agregado'
        verbose_name_plural = 'Precios de Agregados'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.agregado.nombre}: ${self.precio}'

    def save(self, *args, **kwargs):
        # Si es nuevo y no tiene fecha_inicio, usar hoy
        if not self.pk and not self.fecha_inicio:
            self.fecha_inicio = timezone.now().date()
        
        # Si es nuevo y activo, desactivar el anterior
        if not self.pk and self.is_active:
            anteriores = AgregadoPrecio.objects.filter(
                agregado=self.agregado,
                is_active=True
            )
            for anterior in anteriores:
                anterior.is_active = False
                anterior.fecha_fin = timezone.now().date()
                anterior.save()
        
        super().save(*args, **kwargs)