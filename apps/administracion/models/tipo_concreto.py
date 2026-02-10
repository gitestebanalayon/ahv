# apps/administracion/models/tipo_concreto.py
from django.db import models

class TipoConcreto(models.Model):
    codigo = models.CharField('Código', max_length=20, unique=True)
    nombre = models.CharField('Nombre', max_length=255, unique=True)
    descripcion = models.CharField('Descripción', max_length=255, blank=True)
    is_delete = models.BooleanField('Eliminado', default=False)
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha Actualización', auto_now=True)

    class Meta:
        managed = True
        # db_table = 'tipo_concreto'
        db_table = 'administracion\".\"tipo_concreto'
        verbose_name = 'Tipo Concreto'
        verbose_name_plural = 'Tipos de Concretos'

    def __str__(self):
        return self.nombre
    
    # @property
    # def precio_actual(self):
    #     """Obtiene el precio activo actual del agregado"""
    #     precio = self.precios.filter(is_active=True).first()
    #     return precio.precio if precio else 0