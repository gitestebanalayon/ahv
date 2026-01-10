from django.db                                  import models
from django.db.models import Max
from apps.auxiliares.models.estado_pedido       import EstadoPedido
from apps.sistema.models.conductor              import Conductor
from apps.sistema.models.vehiculo               import Vehiculo
from apps.cuenta.models                         import User

class Pedido(models.Model):
    codigo_pedido           = models.CharField('Código de Pedido',     max_length = 20,                          unique=True                                          )
    cliente                 = models.ForeignKey(User,                  on_delete=models.PROTECT,                                      )
    cantidad_yardas         = models.DecimalField('Cantidad de Yardas',       max_digits = 10, decimal_places = 1,                      )
    direccion_entrega       = models.CharField('Dirección Entrega',     max_length = 255,                                                                   )
    
    fecha_entrega           = models.DateField('Fecha Entrega',                                                                                             )
    hora_entrega            = models.TimeField('Hora Entrega',                                                                                              )
    nota                    = models.TextField('Nota',                                                  blank = True,   null = True                  )
    estado_pedido           = models.ForeignKey(EstadoPedido,           on_delete = models.PROTECT, db_column="estado_pedido",     related_name = 'estado_pedido',    to_field = 'nombre',     default = 'pendiente'      )
    
    slump                   = models.IntegerField('Slump', blank = True, null = True)
    agregados               = models.CharField('Agregados',     max_length = 100, blank = True, null = True                                                                  )
    precio_yarda            = models.DecimalField('Precio Yarda',       max_digits = 10, decimal_places = 2,   blank = True, null = True                    )
    precio_total            = models.DecimalField('Precio Total',       max_digits = 10, decimal_places = 2,   blank = True, null = True                    )
    
    is_delete               = models.BooleanField('Es Eliminado',          default = False                            )
    fecha_creacion          = models.DateTimeField('Fecha Creación',        auto_now_add = True                                                             )
    fecha_modificacion      = models.DateTimeField('Fecha Modificación',    auto_now = True                                                                 )
    
    class Meta:
        managed             = True
        db_table            = 'sistema\".\"pedido'
        verbose_name        = 'Pedido'
        verbose_name_plural = 'Pedidos'
        
    def __str__(self):
        return f'{self.codigo_pedido}'
    
    def save(self, *args, **kwargs):
        # Generar código automático solo si es un nuevo registro
        if not self.codigo_pedido:
            # Obtener el último número de pedido
            ultimo_pedido = Pedido.objects.aggregate(max_numero=Max('codigo_pedido'))
            ultimo_numero = 0
            
            if ultimo_pedido['max_numero']:
                # Extraer solo los números del último código
                try:
                    ultimo_numero = int(ultimo_pedido['max_numero'].replace('P', ''))
                except (ValueError, AttributeError):
                    ultimo_numero = 999  # Si hay error, empezar desde 1000
            
            # Si no hay pedidos, empezar desde 1000
            if ultimo_numero < 1000:
                nuevo_numero = 1000
            else:
                nuevo_numero = ultimo_numero + 1
            
            self.codigo_pedido = f'P{nuevo_numero}'
        
        super().save(*args, **kwargs)
    
class Entrega(models.Model):
    codigo_entrega          = models.CharField('Código de Entrega',         max_length = 20,                                                                    )
    pedido                  = models.ForeignKey(Pedido,                     on_delete = models.PROTECT, )
    vehiculo                = models.OneToOneField(Vehiculo,                on_delete=models.PROTECT,    )
    conductor               = models.OneToOneField(Conductor,               on_delete=models.PROTECT,    )
    secuencia               = models.IntegerField('Secuencia de Entrega')
    yardas_asignadas        = models.DecimalField('Yardas Asignadas',       max_digits = 10, decimal_places = 1,                      )
    fecha_entrega           = models.DateField('Fecha Entrega',                                                                                             )
    hora_entrega            = models.TimeField('Hora Entrega',                                                                                              )
    entregado               = models.BooleanField('Es Entregado',          default = False                            )
    nota                    = models.TextField('Nota',                                                  blank = True,   null = True                  )
    is_delete               = models.BooleanField('Es Eliminado',          default = False                            )
    fecha_creacion          = models.DateTimeField('Fecha Creación',        auto_now_add = True                                                             )
    fecha_modificacion      = models.DateTimeField('Fecha Modificación',    auto_now = True                                                                 )
  
    class Meta:
        managed = True
        verbose_name = 'Entrega'
        verbose_name_plural = 'Entregas'
    
    def __str__(self):
        return f'{self.codigo_entrega} - {self.pedido.codigo_pedido}'
  
    def save(self, *args, **kwargs):
        # Generar código automático solo si es un nuevo registro
        if not self.codigo_entrega:
            # Obtener el último número de entrega
            ultima_entrega = Entrega.objects.aggregate(max_numero=Max('codigo_entrega'))
            ultimo_numero = 0
            
            if ultima_entrega['max_numero']:
                # Extraer solo los números del último código
                try:
                    ultimo_numero = int(ultima_entrega['max_numero'].replace('E', ''))
                except (ValueError, AttributeError):
                    ultimo_numero = 999  # Si hay error, empezar desde 1000
            
            # Si no hay entregas, empezar desde 1000
            if ultimo_numero < 1000:
                nuevo_numero = 1000
            else:
                nuevo_numero = ultimo_numero + 1
            
            self.codigo_entrega = f'E{nuevo_numero}'
        
        super().save(*args, **kwargs)