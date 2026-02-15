# utils/mixins/codigo_mixin.py
from django.db import models
from services.codigo_service import CodigoGenerator

class GeneradorCodigoConfigurableMixin(models.Model):
    """
    Mixin configurable con atributos de clase
    """
    class Meta:
        abstract = True
    
    # Configuración por defecto (puedes sobrescribir en cada modelo)
    CODIGO_PREFIJO = ''
    CODIGO_CAMPO = 'codigo'
    CODIGO_MINIMO = 1000
    CODIGO_FILTROS = {}  # Filtros adicionales
    
    def save(self, *args, **kwargs):
        """Guarda generando código automáticamente"""
        self._asignar_codigo_automatico()
        super().save(*args, **kwargs)
    
    def _asignar_codigo_automatico(self):
        """Asigna código si está vacío"""
        if not getattr(self, self.CODIGO_CAMPO):
            generator = CodigoGenerator(
                modelo=self.__class__,
                campo_codigo=self.CODIGO_CAMPO,
                prefijo=self.CODIGO_PREFIJO,
                longitud_minima=self.CODIGO_MINIMO
            )
            
            nuevo_codigo = generator.generar(**self.CODIGO_FILTROS)
            setattr(self, self.CODIGO_CAMPO, nuevo_codigo)