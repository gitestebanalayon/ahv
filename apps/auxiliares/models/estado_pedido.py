from django.db import models
from utils.mixins.atributos_fechas_mixin import FechasAuditoriaMixin
from utils.mixins.borrado_logico_mixin import BorradoLogicoMixin

class EstadoPedido(
        BorradoLogicoMixin,
        FechasAuditoriaMixin, 
        models.Model
    ):
    nombre              = models.CharField('Nombre',        max_length=50,      unique=True             )
    descripcion         = models.CharField('Descripción',   max_length = 100,   unique = True           )
   
    class Meta:
        managed             = True
        # db_table            = 'estado_pedido'
        db_table            = 'auxiliares\".\"estado_pedido'
        verbose_name        = 'Estado Pedido'
        verbose_name_plural = 'Estados Pedidos'

    def __str__(self):
        return f'{self.nombre}'