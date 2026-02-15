# apps/sistema/models/pedido_agregado.py
from django.db import models
from simple_history.models import HistoricalRecords

class PedidoAgregado(models.Model):
    pedido = models.ForeignKey(
        'sistema.Pedido',
        on_delete=models.CASCADE,
        related_name='pedido_agregados_detalle'  # 👈 Nombre diferente
    )
    agregado = models.ForeignKey(
        'administracion.Agregado',
        on_delete=models.PROTECT
    )
    precio_aplicado = models.DecimalField('Precio Aplicado', max_digits=10, decimal_places=2)
    precio_aplicado_codigo = models.CharField('Código Precio', max_length=50, blank=True, null=True)
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    historical = HistoricalRecords()
    
    class Meta:
        managed = True
        db_table = 'sistema\".\"pedido_agregado_precios'  # 👈 Nombre diferente
        unique_together = ['pedido', 'agregado']
        verbose_name = 'Precio de Agregado'
        verbose_name_plural = 'Precios de Agregados'

    def __str__(self):
        return f'{self.pedido.codigo_pedido} - {self.agregado.nombre} (${self.precio_aplicado})'