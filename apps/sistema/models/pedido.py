from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError

from django.db                                  import models
from django.db.models import Max

from apps.auxiliares.models.estado_conductor import EstadoConductor
from apps.auxiliares.models.estado_vehiculo import EstadoVehiculo
from apps.auxiliares.models.estado_pedido       import EstadoPedido
from apps.sistema.models.conductor              import Conductor
from apps.sistema.models.vehiculo               import Vehiculo
from apps.cuenta.models                         import User


class Pedido(models.Model):
    codigo_pedido           = models.CharField('Código de Pedido',     max_length = 20,                          unique=True                                          )
    cliente                 = models.ForeignKey(User,                  on_delete=models.PROTECT,                                      )
    cantidad_yardas         = models.DecimalField('Cantidad de Yardas',       max_digits = 10, decimal_places = 1,                      )
    direccion_entrega       = models.CharField('Dirección Entrega',     max_length = 255,                                                                   )
    
    fecha_entrega           = models.DateField('Fecha Entrega',                                                                                             )
    hora_entrega            = models.TimeField('Hora Entrega',                                                                                              )
    nota                    = models.TextField('Nota',                                                  blank = True,   null = True                  )
    estado_pedido           = models.ForeignKey(EstadoPedido,           on_delete = models.PROTECT, db_column="estado_pedido",     related_name = 'estado_pedido',    to_field = 'nombre',     default = 'pendiente'      )
    
    slump                   = models.IntegerField('Slump', blank = True, null = True)
    agregados               = models.CharField('Agregados',     max_length = 100, blank = True, null = True                                                                  )
    precio_yarda            = models.DecimalField('Precio Yarda',       max_digits = 10, decimal_places = 2,   blank = True, null = True                    )
    precio_total            = models.DecimalField('Precio Total',       max_digits = 10, decimal_places = 2,   blank = True, null = True                    )
    
    is_delete               = models.BooleanField('Es Eliminado',          default = False                            )
    fecha_creacion          = models.DateTimeField('Fecha Creación',        auto_now_add = True                                                             )
    fecha_modificacion      = models.DateTimeField('Fecha Modificación',    auto_now = True                                                                 )
    
    class Meta:
        managed             = True
        db_table            = 'sistema\".\"pedido'
        verbose_name        = 'Pedido'
        verbose_name_plural = 'Pedidos'
        
    def __str__(self):
        return f'{self.codigo_pedido}'
    
    def save(self, *args, **kwargs):
        # Generar código automático solo si es un nuevo registro
        if not self.codigo_pedido:
            # Obtener el último número de pedido
            ultimo_pedido = Pedido.objects.aggregate(max_numero=Max('codigo_pedido'))
            ultimo_numero = 0
            
            if ultimo_pedido['max_numero']:
                # Extraer solo los números del último código
                try:
                    ultimo_numero = int(ultimo_pedido['max_numero'].replace('P', ''))
                except (ValueError, AttributeError):
                    ultimo_numero = 999  # Si hay error, empezar desde 1000
            
            # Si no hay pedidos, empezar desde 1000
            if ultimo_numero < 1000:
                nuevo_numero = 1000
            else:
                nuevo_numero = ultimo_numero + 1
            
            self.codigo_pedido = f'P{nuevo_numero}'
        
        super().save(*args, **kwargs)
    
class Entrega(models.Model):
    ESTADOS_ENTREGA = [
        ('programado', 'Programado'),
        ('en_camino', 'En Camino'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    codigo_entrega          = models.CharField('Código de Entrega',         max_length = 20,                                                                    )
    pedido                  = models.ForeignKey(Pedido,                     on_delete = models.PROTECT, )
    conductor               = models.ForeignKey(Conductor,               on_delete=models.PROTECT,    )
    vehiculo                = models.ForeignKey(Vehiculo,                on_delete=models.PROTECT,    )
    secuencia               = models.IntegerField('Secuencia de Entrega')
    yardas_asignadas        = models.DecimalField('Yardas Asignadas',       max_digits = 10, decimal_places = 1,    validators=[MinValueValidator(0.1)]                  )

    # Cambia estos campos para mejor control
    fecha_hora_salida = models.DateTimeField('Fecha/Hora Salida', null=True, blank=True)
    fecha_hora_entrega = models.DateTimeField('Fecha/Hora Entrega', null=True, blank=True)
    
    estado = models.CharField(
        max_length=20,
        choices=ESTADOS_ENTREGA,
        default='programado'
    )
    
    entregado               = models.BooleanField('Es Entregado',          default = False                            )

    
    nota                    = models.TextField('Nota',                                                  blank = True,   null = True                  )
    is_delete               = models.BooleanField('Es Eliminado',          default = False                            )
    fecha_creacion          = models.DateTimeField('Fecha Creación',        auto_now_add = True                                                             )
    fecha_modificacion      = models.DateTimeField('Fecha Modificación',    auto_now = True                                                                 )
  
    class Meta:
        managed = True
        verbose_name = 'Entrega'
        verbose_name_plural = 'Entregas'
        unique_together = ['pedido', 'secuencia']
    
    def __str__(self):
        return f'{self.codigo_entrega} - {self.pedido.codigo_pedido}'
  
    def clean(self):
        """Validaciones adicionales antes de guardar"""
        if self.yardas_asignadas <= 0:
            raise ValidationError("Las yardas asignadas deben ser mayores a 0")
        
        # # Verificar que conductor esté disponible
        # if not self.pk and self.conductor.estado_conductor_nombre.nombre == 'En Viaje':
        #     raise ValidationError(f"El conductor {self.conductor.nombre} actualmente en un viaje activo")
        
        # # Verificar que vehículo esté disponible
        # if not self.pk and self.vehiculo.estado_vehiculo_nombre.nombre == 'En Viaje':
        #     raise ValidationError(f"El vehículo {self.vehiculo.alias} actualmente en un viaje activo")
  
    def save(self, *args, **kwargs):
         # Validar que yardas_asignadas sea mayor a 0
      
        # Generar código automático solo si es un nuevo registro
        if not self.codigo_entrega:
            # Obtener el último número de entrega
            ultima_entrega = Entrega.objects.aggregate(max_numero=Max('codigo_entrega'))
            ultimo_numero = 0
            
            if ultima_entrega['max_numero']:
                # Extraer solo los números del último código
                try:
                    ultimo_numero = int(ultima_entrega['max_numero'].replace('E', ''))
                except (ValueError, AttributeError):
                    ultimo_numero = 999  # Si hay error, empezar desde 1000
            
            # Si no hay entregas, empezar desde 1000
            if ultimo_numero < 1000:
                nuevo_numero = 1000
            else:
                nuevo_numero = ultimo_numero + 1
            
            self.codigo_entrega = f'E{nuevo_numero}'
            
         # Generar secuencia automática basada en el pedido
        if not self.pk:  # Solo para nuevos registros
            # Obtener la última secuencia para este pedido
            ultima_secuencia = Entrega.objects.filter(
                pedido=self.pedido
            ).aggregate(max_secuencia=Max('secuencia'))
            
            if ultima_secuencia['max_secuencia'] is None:
                # Primera entrega para este pedido
                self.secuencia = 1
            else:
                # Siguiente secuencia
                self.secuencia = ultima_secuencia['max_secuencia'] + 1
        
         # Si es una nueva entrega, marcar conductor y vehículo como ocupados
        # if not self.pk:
        #     try:
        #         # Obtener instancias de los estados
        #         estado_conductor_en_viaje = EstadoConductor.objects.get(nombre='En Viaje')
        #         estado_vehiculo_en_viaje = EstadoVehiculo.objects.get(nombre='En Viaje')
                
        #         # Actualizar estados
        #         self.conductor.estado_conductor_nombre = estado_conductor_en_viaje
        #         self.conductor.save()
                
        #         self.vehiculo.estado_vehiculo_nombre = estado_vehiculo_en_viaje
        #         self.vehiculo.save()
        #     except (EstadoConductor.DoesNotExist, EstadoVehiculo.DoesNotExist) as e:
        #         # Manejar el caso si los estados no existen
        #         raise ValidationError(f"Estado no encontrado: {e}")
        
        super().save(*args, **kwargs)
    
    def marcar_como_iniciado(self):
        """Marca la entrega como iniciada"""
        try:
            # ========== VALIDACIONES ==========
            
            # 1. Validar estado de la entrega
            if self.estado != 'programado':
                raise ValidationError(
                    f"No se puede iniciar la entrega. Estado actual: '{self.get_estado_display()}'. "
                    f"Debe estar en estado 'Programado'."
                )
            
            # 2. Validar que el conductor existe
            if not hasattr(self, 'conductor') or self.conductor is None:
                raise ValidationError("No hay conductor asignado a esta entrega.")
            
            # 3. Validar estado del conductor
            estado_conductor = self.conductor.estado_conductor_nombre.nombre
            if estado_conductor != 'Disponible':
                if estado_conductor == 'En Viaje':
                    raise ValidationError(f"El conductor '{self.conductor.nombre}' está actualmente en otra entrega.")
                elif estado_conductor == 'Descanso':
                    raise ValidationError(f"El conductor '{self.conductor.nombre}' está en descanso.")
                elif estado_conductor == 'Vacaciones':
                    raise ValidationError(f"El conductor '{self.conductor.nombre}' está de vacaciones.")
                else:
                    raise ValidationError(f"El conductor '{self.conductor.nombre}' no está disponible. Estado: '{estado_conductor}'")
            
            # 4. Validar que el vehículo existe
            if not hasattr(self, 'vehiculo') or self.vehiculo is None:
                raise ValidationError("No hay vehículo asignado a esta entrega.")
            
            # 5. Validar estado del vehículo
            estado_vehiculo = self.vehiculo.estado_vehiculo_nombre.nombre
            if estado_vehiculo != 'Disponible':
                if estado_vehiculo == 'En Viaje':
                    raise ValidationError(f"El vehículo '{self.vehiculo.alias}' está actualmente en otra entrega.")
                elif estado_vehiculo == 'Mantenimiento':
                    raise ValidationError(f"El vehículo '{self.vehiculo.alias}' está en mantenimiento.")
                elif estado_vehiculo == 'Reparación':
                    raise ValidationError(f"El vehículo '{self.vehiculo.alias}' está en reparación.")
                else:
                    raise ValidationError(f"El vehículo '{self.vehiculo.alias}' no está disponible. Estado: '{estado_vehiculo}'")
            
            # 6. Validar yardas asignadas
            if not self.yardas_asignadas or float(self.yardas_asignadas) <= 0:
                raise ValidationError("Las yardas asignadas deben ser mayores a 0.")
            
            # ========== EJECUCIÓN ==========
            
            # Obtener estados "En Viaje"
            estado_conductor_en_viaje = EstadoConductor.objects.get(nombre='En Viaje')
            estado_vehiculo_en_viaje = EstadoVehiculo.objects.get(nombre='En Viaje')
            
            # Actualizar estados del conductor y vehículo PRIMERO
            self.conductor.estado_conductor_nombre = estado_conductor_en_viaje
            self.conductor.save()
            
            self.vehiculo.estado_vehiculo_nombre = estado_vehiculo_en_viaje
            self.vehiculo.save()
            
            # Luego actualizar la entrega
            self.estado = 'en_camino'
            self.fecha_hora_salida = timezone.now()
            
            # Agregar nota del inicio
            nota_anterior = self.nota or ""
            self.nota = f"[{timezone.now().strftime('%d/%m/%Y %H:%M:%S')}] INICIADA - Conductor: {self.conductor.nombre}, Vehículo: {self.vehiculo.alias}\n{nota_anterior}"
            
            self.save()
            
        except (EstadoConductor.DoesNotExist, EstadoVehiculo.DoesNotExist) as e:
            raise ValidationError(f"Error del sistema: Estado no configurado. Contacte al administrador.")
        except Exception as e:
            # Re-levantar ValidationError si ya lo es
            if isinstance(e, ValidationError):
                raise e
            # Para otros errores
            raise ValidationError(f"Error al iniciar la entrega: {str(e)}")
    
    def marcar_como_completado(self):
        """Marca la entrega como completada y libera recursos"""
        if self.estado in ['programado', 'en_camino']:
            self.estado = 'entregado'
            self.entregado = True
            self.fecha_hora_entrega = timezone.now()
            
            try:
                # Obtener instancias de los estados disponibles
                estado_conductor_disponible = EstadoConductor.objects.get(nombre='Disponible')
                estado_vehiculo_disponible = EstadoVehiculo.objects.get(nombre='Disponible')
                
                # Liberar conductor y vehículo
                self.conductor.estado_conductor_nombre = estado_conductor_disponible
                self.conductor.save()
                
                self.vehiculo.estado_vehiculo_nombre = estado_vehiculo_disponible
                self.vehiculo.save()
                
                # Verificar si todas las entregas del pedido están completas
                entregas_pendientes = Entrega.objects.filter(
                    pedido=self.pedido,
                    entregado=False
                ).exclude(id=self.id).count()
                
                if entregas_pendientes == 0:
                    # Todas las entregas están completas
                    try:
                        estado_pedido_completado = EstadoPedido.objects.get(nombre='Completado')
                        self.pedido.estado_pedido = estado_pedido_completado
                        self.pedido.save()
                    except EstadoPedido.DoesNotExist:
                        # Si no existe "Completado", usar "Entregado" o similar
                        estado_pedido_entregado = EstadoPedido.objects.get(nombre='Entregado')
                        self.pedido.estado_pedido = estado_pedido_entregado
                        self.pedido.save()
                
                self.save()
                
            except (EstadoConductor.DoesNotExist, EstadoVehiculo.DoesNotExist) as e:
                raise ValidationError(f"Estado no encontrado: {e}")
    
    def cancelar(self):
        """Cancela la entrega y libera recursos"""
        if self.estado in ['programado', 'en_camino']:
            self.estado = 'cancelado'
            
            try:
                # Obtener instancias de los estados disponibles
                estado_conductor_disponible = EstadoConductor.objects.get(nombre='Disponible')
                estado_vehiculo_disponible = EstadoVehiculo.objects.get(nombre='Disponible')
                
                # Liberar conductor y vehículo
                self.conductor.estado_conductor_nombre = estado_conductor_disponible
                self.conductor.save()
                
                self.vehiculo.estado_vehiculo_nombre = estado_vehiculo_disponible
                self.vehiculo.save()
                
                self.fecha_hora_salida = None
                
                self.save()
                
            except (EstadoConductor.DoesNotExist, EstadoVehiculo.DoesNotExist) as e:
                raise ValidationError(f"Estado no encontrado: {e}")
            
    def restablecer(self):
        """Restablece una entrega cancelada a estado programado"""
        if self.estado == 'cancelado':
            self.estado = 'programado'
            self.entregado = False  # Asegurar que se vuelva a False
  
                
            self.save()
        else:
            raise ValidationError(f"No se puede restablecer una entrega en estado '{self.estado}'")