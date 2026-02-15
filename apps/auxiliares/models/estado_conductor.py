from django.db import models
from utils.mixins.atributos_fechas_mixin import FechasAuditoriaMixin
from utils.mixins.borrado_logico_mixin import BorradoLogicoMixin

class EstadoConductor(
        BorradoLogicoMixin,
        FechasAuditoriaMixin,
        models.Model
    ):
    nombre              = models.CharField('Nombre',        max_length=50,      unique=True             )
    descripcion         = models.CharField('Descripción',   max_length = 100,   unique = True           )

    class Meta:
        managed             = True
        # db_table            = 'estado_conductor'
        db_table            = 'auxiliares\".\"estado_conductor'
        verbose_name        = 'Estado Conductor'
        verbose_name_plural = 'Estados Conductores'

    def __str__(self):
        return f'{self.nombre}'