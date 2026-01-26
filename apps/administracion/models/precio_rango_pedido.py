# apps/administracion/models/precio_rango_pedido.py
from django.db import models
from django.utils import timezone
from django.db.models import Max
from apps.administracion.models.rango_pedido import RangoPedido


class PrecioRangoPedido(models.Model):
    codigo = models.IntegerField('Código', unique=True, null=True, blank=True)
    rango_pedido = models.ForeignKey(RangoPedido, on_delete=models.PROTECT, related_name='precios')
    precio_por_yarda = models.DecimalField('Precio por Yarda', max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField('Fecha Inicio', default=timezone.now)
    fecha_fin = models.DateField('Fecha Fin', null=True, blank=True)
    motivo_cambio = models.CharField('Motivo Cambio', max_length=255, blank=True)
    is_delete = models.BooleanField('Eliminado', default=False)
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha Actualización', auto_now=True)

    class Meta:
        db_table = 'precio_rango_pedido'
        verbose_name = 'Precio por Rango de Pedido'
        verbose_name_plural = 'Precios por Rango de Pedido'
        ordering = ['-fecha_inicio']

    def __str__(self):
        return f'{self.rango_pedido.nombre}: ${self.precio_por_yarda}/yd'

    def generar_codigo_automatico(self):
        """Genera un código automático empezando desde 1000"""
        try:
            # Buscar el máximo código existente
            max_codigo = PrecioRangoPedido.objects.aggregate(
                max_codigo=Max('codigo')
            )['max_codigo']
            
            # Si no hay registros, empezar desde 1000
            if max_codigo is None:
                return 1000
            
            # Si el máximo es menor que 1000, empezar desde 1000
            if max_codigo < 1000:
                return 1000
            
            # Incrementar en 1
            return max_codigo + 1
            
        except Exception as e:
            print(f"Error generando código automático: {e}")
            # Si hay error, usar 1000 como valor por defecto
            return 1000

    def save(self, *args, **kwargs):
        # Si es nuevo y no tiene fecha_inicio, usar hoy
        if not self.pk and not self.fecha_inicio:
            self.fecha_inicio = timezone.now().date()
        
        # Generar código automático si no tiene uno
        if not self.codigo:
            self.codigo = self.generar_codigo_automatico()
        
        # Si es nuevo y activo, desactivar el anterior
        if not self.pk:
            anteriores = PrecioRangoPedido.objects.filter(
                rango_pedido=self.rango_pedido,
                fecha_fin__isnull=True,
                is_delete=False
            )
            for anterior in anteriores:
                anterior.fecha_fin = timezone.now().date()
                anterior.save()
        
        super().save(*args, **kwargs)