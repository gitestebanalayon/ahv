# apps/proveedores/models/proveedor_agregado_precio.py
from django.db import models
from datetime import date

from django.db.models import Max, Q
from apps.proveedores.models.proveedor import Proveedor
from apps.administracion.models.agregado import Agregado

class ProveedorAgregadoPrecio(models.Model):
    proveedor = models.ForeignKey(Proveedor, on_delete=models.PROTECT)
    agregado = models.ForeignKey(Agregado, on_delete=models.PROTECT)
    codigo = models.CharField('Código', max_length=20, unique=True)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField('Fecha Inicio', default=date.today)
    fecha_fin = models.DateField('Fecha Fin', null=True, blank=True)
    is_active = models.BooleanField('Activo', default=True)
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha Actualización', auto_now=True)
    
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
        if not self.codigo:
            
            ultimo_codigo = ProveedorAgregadoPrecio.objects.aggregate(
                max_numero=Max('codigo'))
            ultimo_numero = 0

            if ultimo_codigo['max_numero']:
                # Extraer solo los números del último código
                try:
                    ultimo_numero = int(
                        ultimo_codigo['max_numero'].replace('CPA', ''))
                except (ValueError, AttributeError):
                    ultimo_numero = 999  # Si hay error, empezar desde 1000

            # Si no hay entregas, empezar desde 1000
            if ultimo_numero < 1000:
                nuevo_numero = 1000
            else:
                nuevo_numero = ultimo_numero + 1

            self.codigo = f'CPA{nuevo_numero}'
        
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