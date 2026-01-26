# apps/administracion/models/rango_pedido.py
from django.db import models
from django.db.models import Max


class RangoPedido(models.Model):
    codigo = models.IntegerField('Código', unique=True, null=True, blank=True)
    nombre = models.CharField('Nombre', max_length=50, unique=True)
    yarda_minima = models.DecimalField('Yarda Mínima', max_digits=10, decimal_places=1)
    yarda_maxima = models.DecimalField('Yarda Máxima', max_digits=10, decimal_places=1, null=True, blank=True)
    descripcion = models.TextField('Descripción', blank=True)
    is_delete = models.BooleanField('Eliminado', default=False)
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha Actualización', auto_now=True)

    class Meta:
        db_table = 'rango_pedido'
        verbose_name = 'Rango de Pedido'
        verbose_name_plural = 'Rangos de Pedido'

    def __str__(self):
        if self.yarda_maxima:
            return f'{self.nombre} ({self.yarda_minima} - {self.yarda_maxima} yardas)'
        return f'{self.nombre} ({self.yarda_minima}+ yardas)'
    
    def contiene_yardas(self, cantidad_yardas):
        """Verifica si una cantidad de yardas está en este rango"""
        if self.yarda_maxima:
            return self.yarda_minima <= cantidad_yardas <= self.yarda_maxima
        return cantidad_yardas >= self.yarda_minima
    
    def generar_codigo_automatico(self):
        """Genera un código automático empezando desde 1000"""
        try:
            # Buscar el máximo código existente (excluyendo eliminados)
            max_codigo = RangoPedido.objects.filter(is_delete=False).aggregate(
                max_codigo=Max('codigo')
            )['max_codigo']
            
            # Si no hay registros activos, buscar en todos
            if max_codigo is None:
                max_codigo = RangoPedido.objects.all().aggregate(
                    max_codigo=Max('codigo')
                )['max_codigo']
            
            # Si no hay registros, empezar desde 1000
            if max_codigo is None:
                return 1000
            
            # Si el máximo es menor que 1000, empezar desde 1000
            if max_codigo < 1000:
                return 1000
            
            # Incrementar en 1
            return max_codigo + 1
            
        except Exception as e:
            print(f"Error generando código automático: {e}")
            # Si hay error, usar 1000 como valor por defecto
            return 1000
    
    def save(self, *args, **kwargs):
        # Generar código automático si no tiene uno y no está siendo eliminado
        if not self.codigo and not self.is_delete:
            self.codigo = self.generar_codigo_automatico()
        
        super().save(*args, **kwargs)