from django.db import models

class Agregado(models.Model):
    nombre              = models.CharField('Nombre',        max_length=50,      unique=True             )
    descripcion         = models.CharField('Descripción',   max_length = 100,   unique = True           )
    costo               = models.DecimalField('Costo',       max_digits=10,       decimal_places=2      )
    is_delete           = models.BooleanField('Es Eliminado',          default = False                  )
    fecha_creacion      = models.DateTimeField('Fecha Creación',        auto_now_add = True             )
    fecha_modificacion  = models.DateTimeField('Fecha Modificación',    auto_now = True                 )

    class Meta:
        managed             = True
        # db_table            = 'auxiliares\".\"estado_pedido'
        db_table            = 'agregado'
        verbose_name        = 'Agregado'
        verbose_name_plural = 'Agregados'

    def __str__(self):
        return f'{self.nombre}'