# apps/sistema/models/agregado_pedido.py
from django.db import models
from apps.administracion.models.agregado import Agregado
from apps.sistema.models.pedido import Pedido


class AgregadoPedido(models.Model):
    agregado = models.ForeignKey(Agregado, on_delete=models.PROTECT)
    pedido = models.ForeignKey(Pedido, on_delete=models.PROTECT, related_name='agregados_pedido')
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha Actualización', auto_now=True)

    class Meta:
        db_table = 'sistema\".\"agregado_pedido'
        verbose_name = 'Agregado del Pedido'
        verbose_name_plural = 'Agregados del Pedido'
        unique_together = ['agregado', 'pedido']

    def __str__(self):
        return f'{self.agregado.nombre} - {self.pedido.codigo_pedido}'