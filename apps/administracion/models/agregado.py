# apps/administracion/models/agregado.py
from django.db import models
from utils.mixins.atributos_fechas_mixin import FechasAuditoriaMixin
from utils.mixins.borrado_logico_mixin import BorradoLogicoMixin

class Agregado(
        BorradoLogicoMixin,
        FechasAuditoriaMixin,
        models.Model
    ):
    nombre = models.CharField('Nombre', max_length=50, unique=True)
    descripcion = models.CharField('Descripción', max_length=255, blank=True)

    class Meta:
        managed = True
        # db_table = 'agregado'
        db_table = 'administracion\".\"agregado'
        verbose_name = 'Agregado'
        verbose_name_plural = 'Agregados'

    def __str__(self):
        return self.nombre
    
    @property
    def precio_actual(self):
        """Obtiene el precio activo actual del agregado"""
        precio = self.precios.filter(is_active=True).first()
        return precio.precio if precio else 0