# apps/proveedores/models/proveedor.py
from django.db import models
from utils.mixins.atributos_fechas_mixin        import FechasAuditoriaMixin
from utils.mixins.borrado_logico_mixin          import BorradoLogicoMixin
from simple_history.models import HistoricalRecords

class Proveedor(
        BorradoLogicoMixin,
        FechasAuditoriaMixin,
        models.Model
    ):
    nombre_comercial = models.CharField('Nombre', max_length=50, unique=True)
    historical = HistoricalRecords()

    class Meta:
        managed = True
        db_table = 'proveedores\".\"proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre_comercial
    
    