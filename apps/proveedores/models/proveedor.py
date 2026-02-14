# apps/proveedores/models/proveedor.py
from django.db import models

class Proveedor(models.Model):
    nombre_comercial = models.CharField('Nombre', max_length=50, unique=True)
    is_delete = models.BooleanField('Eliminado', default=False)
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha Actualización', auto_now=True)

    class Meta:
        managed = True
        db_table = 'proveedores\".\"proveedor'
        verbose_name = 'Proveedor'
        verbose_name_plural = 'Proveedores'

    def __str__(self):
        return self.nombre_comercial
    
    