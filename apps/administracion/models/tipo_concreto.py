# apps/administracion/models/tipo_concreto.py
from django.db import models
from django.db.models import Max
from datetime import date

class TipoConcreto(models.Model):
    codigo = models.CharField('Código', max_length=20, unique=True)
    nombre = models.CharField('Nombre', max_length=255, unique=True)
    descripcion = models.CharField('Descripción', max_length=255, blank=True)
    is_delete = models.BooleanField('Eliminado', default=False)
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(
        'Fecha Actualización', auto_now=True)

    class Meta:
        managed = True
        # db_table = 'tipo_concreto'
        db_table = 'administracion\".\"tipo_concreto'
        verbose_name = 'Tipo Concreto'
        verbose_name_plural = 'Tipos de Concretos'

    def __str__(self):
        return self.nombre

    

    def save(self, *args, **kwargs):
        # Generar código automático solo si es un nuevo registro
        if not self.codigo:
            # Obtener el último número de entrega
            ultimo_codigo = TipoConcreto.objects.aggregate(
                max_numero=Max('codigo'))
            ultimo_numero = 0

            if ultimo_codigo['max_numero']:
                # Extraer solo los números del último código
                try:
                    ultimo_numero = int(
                        ultimo_codigo['max_numero'].replace('C', ''))
                except (ValueError, AttributeError):
                    ultimo_numero = 999  # Si hay error, empezar desde 1000

            # Si no hay entregas, empezar desde 1000
            if ultimo_numero < 1000:
                nuevo_numero = 1000
            else:
                nuevo_numero = ultimo_numero + 1

            self.codigo = f'C{nuevo_numero}'
        
        super().save(*args, **kwargs)

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
