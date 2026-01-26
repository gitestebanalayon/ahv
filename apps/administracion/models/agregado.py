# apps/administracion/models/agregado.py
from django.db import models

class Agregado(models.Model):
    nombre = models.CharField('Nombre', max_length=50, unique=True)
    descripcion = models.CharField('Descripción', max_length=255, blank=True)
    is_delete = models.BooleanField('Eliminado', default=False)
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha Actualización', auto_now=True)

    class Meta:
        db_table = 'agregado'
        verbose_name = 'Agregado'
        verbose_name_plural = 'Agregados'

    def __str__(self):
        return self.nombre
    
    @property
    def precio_actual(self):
        """Obtiene el precio activo actual del agregado"""
        precio = self.precios.filter(is_active=True).first()
        return precio.precio if precio else 0