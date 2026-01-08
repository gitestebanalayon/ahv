from django.db                                  import models
from apps.auxiliares.models.estado_conductor    import EstadoConductor
from apps.sistema.models.vehiculo               import Vehiculo

class Conductor(models.Model):
    vehiculo                = models.OneToOneField(Vehiculo,               on_delete=models.PROTECT,       related_name='vehiculo',  null=True, blank=True)
    nombre                  = models.CharField('Nombre',                max_length = 100,                                       )
    licencia                = models.CharField('Licencia',              max_length = 50,    unique = True                       )
    telefono                = models.CharField('Teléfono',              max_length = 15,                                        )    
    estado_conductor_nombre = models.ForeignKey(EstadoConductor,        on_delete = models.PROTECT, db_column="estado_conductor",     related_name = 'estado_conductor',    to_field = 'nombre', default = 'disponible'   )
    is_delete               = models.BooleanField('Es Eliminado',          default = False                            )
    fecha_creacion          = models.DateTimeField('Fecha Creación',        auto_now_add = True                                 )
    fecha_modificacion      = models.DateTimeField('Fecha Modificación',    auto_now = True                                     )
    
    class Meta:
        managed             = True
        db_table            = 'sistema\".\"conductor'
        verbose_name        = 'Conductor'
        verbose_name_plural = 'Conductores'
        
    def __str__(self):
        return f'{self.nombre}'