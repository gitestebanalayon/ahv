# apps/proveedores/models/proveedor_tipoconcreto_precio.py
from django.db import models
from datetime import date

from django.db.models import Max, Q
from apps.proveedores.models.proveedor import Proveedor
from apps.administracion.models.tipo_concreto import TipoConcreto

from utils.mixins.atributos_fechas_mixin        import AtributosFechasMixin
from utils.mixins.codigo_mixin                  import GeneradorCodigoConfigurableMixin

class ProveedorTipoConcretoPrecio(
        GeneradorCodigoConfigurableMixin,
        AtributosFechasMixin,
        models.Model
    ):
    
    CODIGO_PREFIJO = 'CPC'
    CODIGO_MINIMO = 1000
    
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    tipo_concreto = models.ForeignKey(TipoConcreto, on_delete=models.PROTECT)
    codigo = models.CharField('Código', max_length=20, unique=True)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    is_active = models.BooleanField('Activo', default=True)
    
    class Meta:
        managed = True
        db_table = 'proveedores\".\"tipo_concreto_precio'
        verbose_name = 'Precio de Tipo Concreto'
        verbose_name_plural = 'Precios de Tipos de Concretos'

        # 👇 ESTO ES LO QUE NECESITAS
        constraints = [
            models.UniqueConstraint(
                fields=['proveedor', 'tipo_concreto'],
                name='unique_proveedor_tipo_concreto_activo',
                condition=Q(is_active=True)  # Solo aplica cuando is_active=True
            )
        ]

    def __str__(self):
        return f'{self.proveedor.nombre_comercial} {self.tipo_concreto.nombre} {self.precio} {self.fecha_inicio} {self.fecha_fin}'
    
    def save(self, *args, **kwargs):
        # Si es nuevo y activo, desactivar el anterior
        if not self.pk:
            anteriores = ProveedorTipoConcretoPrecio.objects.filter(
                proveedor=self.proveedor,
                tipo_concreto=self.tipo_concreto,
                fecha_fin__isnull=True,
                is_active=True
            )
            for anterior in anteriores:
                anterior.is_active = False
                anterior.fecha_fin = date.today()
                anterior.save()
        
        super().save(*args, **kwargs)