# utils/mixins/borrado_logico_mixin.py
from django.db import models
from datetime import date

class BorradoLogicoMixin(models.Model):
    """Borrado Lógico"""
    class Meta:
        abstract = True
    
    is_delete = models.BooleanField('Eliminado', default=False)