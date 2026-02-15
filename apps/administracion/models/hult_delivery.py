# apps/administracion/models/rango_pedido.py
from django.db import models
from django.db.models import Max
from datetime import date
from utils.mixins.atributos_fechas_mixin import FechasAuditoriaMixin
from utils.mixins.borrado_logico_mixin import BorradoLogicoMixin

class HultDelivery(
        BorradoLogicoMixin,
        FechasAuditoriaMixin,
        models.Model
    ):
    nombre = models.CharField('Nombre', max_length=50, unique=True)
    yarda_minima = models.DecimalField('Yarda Mínima', max_digits=10, decimal_places=1)
    yarda_maxima = models.DecimalField('Yarda Máxima', max_digits=10, decimal_places=1, null=True, blank=True)

    class Meta:
        managed = True
        # db_table = 'rango_pedido'
        db_table = 'administracion\".\"hult_delivery'
        verbose_name = 'Hult Delivery'
        verbose_name_plural = 'Hults Deliverys'

    def __str__(self):
        if self.yarda_maxima:
            return f'{self.nombre} ({self.yarda_minima} - {self.yarda_maxima} yardas)'
        return f'{self.nombre} ({self.yarda_minima}+ yardas)'
    
    def verificar_rango_delivery(self, cantidad_yardas):
        """Verifica si una cantidad de yardas está en el rango de hult delivery"""
        if self.yarda_maxima:
            return self.yarda_minima <= cantidad_yardas <= self.yarda_maxima
        return cantidad_yardas >= self.yarda_minima
    
    @property    
    def precio_actual(self):
        """Obtiene el precio activo actual del hult delivery"""
        precio = self.preciohultdelivery_set.filter(
            is_active=True,
            fecha_inicio__lte=date.today()
        ).order_by('-fecha_inicio').first()
        return precio.precio if precio else 0
    
  