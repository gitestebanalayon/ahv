from django.db                                  import models
from apps.auxiliares.models.estado_pedido       import EstadoPedido
from apps.sistema.models.conductor              import Conductor
from apps.sistema.models.vehiculo               import Vehiculo
from apps.cuenta.models                         import User

class Pedido(models.Model):
    cliente                 = models.ForeignKey(User,                  on_delete=models.PROTECT,                                      )
    conductor               = models.OneToOneField(Conductor,             on_delete=models.PROTECT,           null=True, blank=True   )
    vehiculo                = models.OneToOneField(Vehiculo,              on_delete=models.PROTECT,           null=True, blank=True   )
    fecha_entrega           = models.DateField('Fecha Entrega',                                                                                             )
    hora_entrega            = models.TimeField('Hora Entrega',                                                                                              )
    direccion_entrega       = models.CharField('Dirección Entrega',     max_length = 255,                                                                   )
    observacion             = models.TextField('Observación',                                                  blank = True,   null = True                  )
    estado_pedido_nombre    = models.ForeignKey(EstadoPedido,           on_delete = models.PROTECT, db_column="estado_pedido",     related_name = 'estado_pedido',    to_field = 'nombre',     default = 'pendiente'      )
    
    total_yardas            = models.DecimalField('Total Yardas',       max_digits = 10, decimal_places = 1,   blank = True, null = True                    )
    precio_yarda            = models.DecimalField('Precio Yarda',       max_digits = 10, decimal_places = 2,   blank = True, null = True                    )
    precio_total            = models.DecimalField('Precio Total',       max_digits = 10, decimal_places = 2,   blank = True, null = True                    )
  
    fecha_creacion          = models.DateTimeField('Fecha Creación',        auto_now_add = True                                                             )
    fecha_modificacion      = models.DateTimeField('Fecha Modificación',    auto_now = True                                                                 )
    
    class Meta:
        managed             = True
        db_table            = 'sistema\".\"pedido'
        verbose_name        = 'Pedido'
        verbose_name_plural = 'Pedidos'
        
    def __str__(self):
        return f'{self.cliente.username} - {self.estado_pedido_nombre}'