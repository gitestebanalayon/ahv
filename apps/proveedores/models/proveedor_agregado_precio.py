# apps/proveedores/models/proveedor_agregado_precio.py
from django.db import models
from datetime import date

from django.db.models import Max, Q
from apps.proveedores.models.proveedor import Proveedor
from apps.administracion.models.agregado import Agregado

from utils.mixins.atributos_fechas_mixin        import AtributosFechasMixin
from utils.mixins.codigo_mixin                  import GeneradorCodigoConfigurableMixin
from simple_history.models import HistoricalRecords

class ProveedorAgregadoPrecio(
        GeneradorCodigoConfigurableMixin,
        AtributosFechasMixin,
        models.Model
    ):
    
    CODIGO_PREFIJO = 'CPA'
    CODIGO_MINIMO = 1000
    
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    agregado = models.ForeignKey(Agregado, on_delete=models.PROTECT)
    codigo = models.CharField('Código', max_length=20, unique=True)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    is_active = models.BooleanField('Activo', default=True)
    historical = HistoricalRecords()
    
    class Meta:
        managed = True
        db_table = 'proveedores\".\"agregado_precio'
        verbose_name = 'Precio de Agregado'
        verbose_name_plural = 'Precios de Agregados'
        
        constraints = [
            models.UniqueConstraint(
                fields=['proveedor', 'agregado'],
                name='unique_proveedor_agregado_activo',
                condition=Q(is_active=True)  # Solo aplica cuando is_active=True
            )
        ]

    def __str__(self):
        return f'{self.proveedor.nombre_comercial} {self.agregado.nombre} {self.precio} {self.fecha_inicio} {self.fecha_fin}'
    
    def save(self, *args, **kwargs):    
        # Si es nuevo y activo, desactivar el anterior
        if not self.pk:
            anteriores = ProveedorAgregadoPrecio.objects.filter(
                proveedor=self.proveedor,
                agregado=self.agregado,
                fecha_fin__isnull=True,
                is_active=True
            )
            for anterior in anteriores:
                anterior.is_active = False
                anterior.fecha_fin = date.today()
                anterior.save()
        
        super().save(*args, **kwargs)