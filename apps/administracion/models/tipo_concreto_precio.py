# apps/administracion/models/tipo_concreto_precio.py
from django.db import models
from django.db.models import Max
from datetime import date
from apps.administracion.models.tipo_concreto import TipoConcreto

class TipoConcretoPrecio(models.Model):
    tipo_concreto = models.ForeignKey(TipoConcreto, on_delete=models.PROTECT)
    codigo = models.CharField('Código', max_length=20, unique=True)
    precio = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField('Fecha Inicio', default=date.today)
    fecha_fin = models.DateField('Fecha Fin', null=True, blank=True)
    motivo_cambio = models.CharField('Motivo Cambio', max_length=255, blank=True)
    is_active = models.BooleanField('Activo', default=True)
    fecha_creacion = models.DateTimeField('Fecha Creación', auto_now_add=True)
    fecha_actualizacion = models.DateTimeField('Fecha Actualización', auto_now=True)

    class Meta:
        managed = True
        db_table = 'administracion\".\"tipo_concreto_precio'
        verbose_name = 'Tipo de concreto precio'
        verbose_name_plural = 'Tipos de concretos precios'

    def __str__(self):
        return f'{self.precio} {self.fecha_inicio} {self.fecha_fin}'
    
    def save(self, *args, **kwargs):
        
        # Generar código automático solo si es un nuevo registro
        if not self.codigo:
            # Obtener el último número de entrega
            ultimo_codigo = TipoConcretoPrecio.objects.aggregate(
                max_numero=Max('codigo'))
            ultimo_numero = 0

            if ultimo_codigo['max_numero']:
                # Extraer solo los números del último código
                try:
                    ultimo_numero = int(
                        ultimo_codigo['max_numero'].replace('CP', ''))
                except (ValueError, AttributeError):
                    ultimo_numero = 999  # Si hay error, empezar desde 1000

            # Si no hay entregas, empezar desde 1000
            if ultimo_numero < 1000:
                nuevo_numero = 1000
            else:
                nuevo_numero = ultimo_numero + 1

            self.codigo = f'CP{nuevo_numero}'
        
        # Si es nuevo y no tiene fecha_inicio, usar hoy
        # if not self.pk and not self.fecha_inicio:
        #     self.fecha_inicio = timezone.now().date()
        
        # Si es nuevo y activo, desactivar el anterior
        if not self.pk:
            anteriores = TipoConcretoPrecio.objects.filter(
                tipo_concreto=self.tipo_concreto,
                fecha_fin__isnull=True,
                is_active=True
            )
            for anterior in anteriores:
                anterior.is_active = False
                anterior.fecha_fin = date.today()
                anterior.save()
        
        super().save(*args, **kwargs)