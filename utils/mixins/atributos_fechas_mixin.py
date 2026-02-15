# utils/mixins/atributos_fechas_mixin.py
from django.db import models
from datetime import date

class FechasHistoricasMixin(models.Model):
    """Solo fechas para histórico (inicio/fin)"""
    class Meta:
        abstract = True
    
    fecha_inicio = models.DateField('Fecha Inicio', default=date.today)
    fecha_fin = models.DateField('Fecha Fin', null=True, blank=True)

class FechasAuditoriaMixin(models.Model):
    """Solo fechas de auditoría (creación/actualización)"""
    class Meta:
        abstract = True
    
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    fecha_modificacion = models.DateTimeField('Fecha Modificación', auto_now=True)

class AtributosFechasMixin(FechasHistoricasMixin, FechasAuditoriaMixin):
    """Mixin completo que combina ambos (opcional)"""
    class Meta:
        abstract = True