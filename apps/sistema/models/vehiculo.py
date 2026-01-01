from django.db                                  import models
from apps.auxiliares.models.estado_vehiculo     import EstadoVehiculo

class Vehiculo(models.Model):
    matricula               = models.CharField('Matrícula',                max_length = 15,   unique = True                     )
    alias                   = models.CharField('Alias',                    max_length = 50,                                     )
    estado_vehiculo_nombre  = models.ForeignKey(EstadoVehiculo,            on_delete = models.PROTECT, db_column='estado_vehiculo',    related_name = 'estado_vehiculo',    to_field = 'nombre',   default = 'disponible'   )
    fecha_creacion      = models.DateTimeField('Fecha Creación',        auto_now_add = True                                     )
    fecha_modificacion  = models.DateTimeField('Fecha Modificación',    auto_now = True                                         )
    
    class Meta:
        managed             = True
        db_table            = 'sistema\".\"vehiculo'
        verbose_name        = 'Vehículo'
        verbose_name_plural = 'Vehículos'
        
    def __str__(self):
        return f'{self.alias}'