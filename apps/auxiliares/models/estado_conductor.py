from django.db import models

class EstadoConductor(models.Model):
    nombre              = models.CharField('Nombre',        max_length=50,      unique=True             )
    descripcion         = models.CharField('Descripción',   max_length = 100,   unique = True           )
    is_delete           = models.BooleanField('Es Eliminado',               default = False             )
    fecha_creacion      = models.DateTimeField('Fecha Creación',        auto_now_add = True             )
    fecha_modificacion  = models.DateTimeField('Fecha Modificación',    auto_now = True                 )

    class Meta:
        managed             = True
        # db_table            = 'auxiliares\".\"estado_conductor'
        db_table            = 'estado_conductor'
        verbose_name        = 'Estado Conductor'
        verbose_name_plural = 'Estados Conductores'

    def __str__(self):
        return f'{self.nombre}'