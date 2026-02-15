# apps/administracion/models/tipo_concreto.py
from django.db import models
from django.db.models import Max
from datetime import date
from utils.mixins.atributos_fechas_mixin import FechasAuditoriaMixin
from utils.mixins.borrado_logico_mixin import BorradoLogicoMixin
from utils.mixins.codigo_mixin import GeneradorCodigoConfigurableMixin
from simple_history.models import HistoricalRecords

class TipoConcreto(
        GeneradorCodigoConfigurableMixin,
        BorradoLogicoMixin,
        FechasAuditoriaMixin,
        models.Model
    ):
    
    CODIGO_PREFIJO = 'C'
    CODIGO_MINIMO = 1000
    
    codigo = models.CharField('Código', max_length=20, unique=True)
    nombre = models.CharField('Nombre', max_length=255, unique=True)
    descripcion = models.CharField('Descripción', max_length=255, blank=True)
    historical = HistoricalRecords()

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
    #     precio = self.tipoconcretoprecio_set.filter(is_active=True).first()
    #     return precio.precio if precio else 0
    
    @property    
    def precio_actual(self):
        """Obtiene el precio activo actual del tipo de concreto"""
        precio = self.tipoconcretoprecio_set.filter(
            is_active=True,
            fecha_inicio__lte=date.today()
        ).order_by('-fecha_inicio').first()
        return precio.precio if precio else 0
    
    # @property
    # def precio_actual_obj(self):
    #     """Obtiene el objeto completo del precio activo actual"""
    #     return self.tipoconcretoprecio_set.filter(
    #         is_active=True,
    #         fecha_inicio__lte=date.today()
    #     ).order_by('-fecha_inicio').first()
