from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError


from django.db                                  import models
from django.db.models import Max, Sum

from apps.auxiliares.models.agregado import Agregado
from apps.auxiliares.models.estado_conductor import EstadoConductor
from apps.auxiliares.models.estado_vehiculo import EstadoVehiculo
from apps.auxiliares.models.estado_pedido       import EstadoPedido
from apps.sistema.models.conductor              import Conductor
from apps.sistema.models.vehiculo               import Vehiculo
from apps.cuenta.models                         import User


class Pedido(models.Model):
    codigo_pedido           = models.CharField('Número de Orden',     max_length = 20,                          unique=True                                          )
    cliente                 = models.ForeignKey(User,                  on_delete=models.PROTECT,                                      )
    cantidad_yardas         = models.DecimalField('Cantidad de Yardas',       max_digits = 10, decimal_places = 1,                      )
    direccion_entrega       = models.CharField('Dirección Entrega',     max_length = 255,                                                                   )
    
    fecha_entrega           = models.DateField('Fecha Entrega',                                                                                             )
    hora_entrega            = models.TimeField('Hora Entrega',                                                                                              )
    nota                    = models.TextField('Nota',                                                  blank = True,   null = True                  )
    estado_pedido           = models.ForeignKey(EstadoPedido,           on_delete = models.PROTECT, db_column="estado_pedido",     related_name = 'estado_pedido',    to_field = 'nombre',     default = 'pendiente'      )
    
    slump                   = models.IntegerField('Slump', blank = True, null = True)
    agregado = models.ManyToManyField(
        Agregado, 
        verbose_name='Agregados',
        blank=True,
        null=True,
        # Opcional: si quieres personalizar el nombre de la tabla intermedia
        # through='AgregadoPedido'
    )
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
            
            self.codigo_pedido = f'N{nuevo_numero}'
        
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
        
        
        # Guardar primero la entrega para que se cuente en las consultas
        super().save(*args, **kwargs)
            
        # Verificar si se han completado todas las entregas del pedido
        if self.pedido:
            # Recalcular después del guardado
            todas_entregas = Entrega.objects.filter(pedido=self.pedido)
            total_asignado = todas_entregas.aggregate(
                total=Sum('yardas_asignadas')
            )['total'] or 0
            
            cantidad_requerida = self.pedido.cantidad_yardas
            
            # Verificar si se han asignado suficientes yardas
            if total_asignado >= cantidad_requerida:
                # Obtener estado 'Programado'
                try:
                    estado_programado = EstadoPedido.objects.get(nombre='Programado')
                    
                    # Solo cambiar si no está ya en estado 'Programado' o superior
                    estados_avanzados = ['Programado', 'En Viaje', 'Completado', 'Entregado']
                    if self.pedido.estado_pedido.nombre not in estados_avanzados:
                        self.pedido.estado_pedido = estado_programado
                        self.pedido.save()
                        
                        # Log para depuración
                        # print(f"📦 Pedido {self.pedido.codigo_pedido} actualizado a 'Programado'")
                        # print(f"   - Yardas requeridas: {cantidad_requerida}")
                        # print(f"   - Yardas asignadas: {total_asignado}")
                        # print(f"   - Entregas creadas: {todas_entregas.count()}")
                except EstadoPedido.DoesNotExist:
                    print("⚠️ Estado 'Programado' no encontrado en la base de datos")
        
               

        
     
    
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
            
            # marcar estado del pedido como 'En Viaje' cuando una sola entrega inicia
            estado_pedido_en_viaje = EstadoPedido.objects.get(nombre='En Viaje')
            if self.pedido.estado_pedido.nombre != 'En Viaje':
                self.pedido.estado_pedido = estado_pedido_en_viaje
                self.pedido.save()
        


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
                
                    estado_pedido_completado = EstadoPedido.objects.get(nombre='Completado')
                    self.pedido.estado_pedido = estado_pedido_completado
                    self.pedido.save()
              
                self.save()
                
            except (EstadoConductor.DoesNotExist, EstadoVehiculo.DoesNotExist) as e:
                raise ValidationError(f"Estado no encontrado: {e}")
    
    def cancelar(self):
        """Cancela la entrega y libera recursos"""
        if self.estado in ['programado', 'en_camino']:
            self.estado = 'cancelado'
            
            try:
                # Liberar conductor y vehículo si están asignados
                if self.conductor and self.vehiculo:
                    estado_conductor_disponible = EstadoConductor.objects.get(nombre='Disponible')
                    estado_vehiculo_disponible = EstadoVehiculo.objects.get(nombre='Disponible')
                    
                    self.conductor.estado_conductor_nombre = estado_conductor_disponible
                    self.conductor.save()
                    
                    self.vehiculo.estado_vehiculo_nombre = estado_vehiculo_disponible
                    self.vehiculo.save()
                
                self.fecha_hora_salida = None
                self.save()
                
                # ACTUALIZACIÓN: VERIFICAR ESTADO DEL PEDIDO DESPUÉS DE CANCELAR
                entregas_activas = Entrega.objects.filter(
                    pedido=self.pedido
                ).exclude(estado='cancelado')
                
                # Verificar si hay entregas en viaje
                entregas_en_viaje = entregas_activas.filter(estado='en_camino').exists()
                
                if entregas_en_viaje:
                    # Si hay entregas en viaje, mantener el pedido en "En Viaje"
                    estado_pedido_en_viaje = EstadoPedido.objects.get(nombre='En Viaje')
                    if self.pedido.estado_pedido.nombre != 'En Viaje':
                        self.pedido.estado_pedido = estado_pedido_en_viaje
                        self.pedido.save()
                        print(f"✅ Pedido mantenido en 'En Viaje' después de cancelar entrega")
                
                # Solo marcar como "Pendiente" si NO hay entregas en viaje
                elif entregas_activas.count() == 0:
                    estado_pedido_pendiente = EstadoPedido.objects.get(nombre='Pendiente')
                    if self.pedido.estado_pedido.nombre != 'Pendiente':
                        self.pedido.estado_pedido = estado_pedido_pendiente
                        self.pedido.save()
                        print(f"✅ Pedido actualizado a 'Pendiente' (todas las entregas canceladas)")
                
            except (EstadoConductor.DoesNotExist, EstadoVehiculo.DoesNotExist) as e:
                raise ValidationError(f"Estado no encontrado: {e}")
            
    def restablecer(self):
        """Restablece una entrega cancelada a estado programado"""
        if self.estado == 'cancelado':
            self.estado = 'programado'
            self.entregado = False
            
            # Guardar primero el cambio en la entrega
            self.save()
            
            # VERIFICAR EL ESTADO ACTUAL DEL PEDIDO ANTES DE CAMBIARLO
            # 1. Obtener todas las entregas del pedido (excluyendo canceladas)
            entregas_activas = Entrega.objects.filter(
                pedido=self.pedido
            ).exclude(estado='cancelado')
            
            # 2. Verificar si hay alguna entrega "En Viaje"
            entregas_en_viaje = entregas_activas.filter(estado='en_camino').exists()
            entregas_programadas = entregas_activas.filter(estado='programado').exists()
            entregas_entregadas = entregas_activas.filter(estado='entregado')
            
            # 3. Verificar si todas las entregas están entregadas
            todas_entregadas = entregas_entregadas.count() == entregas_activas.count()
            
            # 4. Determinar el estado correcto del pedido
            try:
                if entregas_en_viaje:
                    # Si hay alguna entrega en viaje, el pedido debe estar "En Viaje"
                    estado_pedido_en_viaje = EstadoPedido.objects.get(nombre='En Viaje')
                    if self.pedido.estado_pedido.nombre != 'En Viaje':
                        self.pedido.estado_pedido = estado_pedido_en_viaje
                        self.pedido.save()
                        print(f"✅ Pedido {self.pedido.codigo_pedido} actualizado a 'En Viaje' (hay entregas en camino)")
                
                elif todas_entregadas:
                    # Si todas las entregas están entregadas, el pedido debe estar "Completado"
                    estado_pedido_completado = EstadoPedido.objects.get(nombre='Completado')
                    if self.pedido.estado_pedido.nombre != 'Completado':
                        self.pedido.estado_pedido = estado_pedido_completado
                        self.pedido.save()
                        print(f"✅ Pedido {self.pedido.codigo_pedido} actualizado a 'Completado' (todas entregadas)")
                
                elif entregas_programadas:
                    # Si hay entregas programadas pero ninguna en viaje
                    # Verificar si se han asignado todas las yardas
                    total_yardas_activas = entregas_activas.aggregate(
                        total=Sum('yardas_asignadas')
                    )['total'] or 0
                    
                    if total_yardas_activas >= self.pedido.cantidad_yardas:
                        # Yardas completas -> Pedido "Programado"
                        estado_pedido_programado = EstadoPedido.objects.get(nombre='Programado')
                        if self.pedido.estado_pedido.nombre != 'Programado':
                            self.pedido.estado_pedido = estado_pedido_programado
                            self.pedido.save()
                            print(f"✅ Pedido {self.pedido.codigo_pedido} actualizado a 'Programado' (yardas completas)")
                    else:
                        # Yardas incompletas -> Pedido "Pendiente"
                        estado_pedido_pendiente = EstadoPedido.objects.get(nombre='Pendiente')
                        if self.pedido.estado_pedido.nombre != 'Pendiente':
                            self.pedido.estado_pedido = estado_pedido_pendiente
                            self.pedido.save()
                            print(f"✅ Pedido {self.pedido.codigo_pedido} actualizado a 'Pendiente' (faltan yardas)")
                
                else:
                    # Caso por defecto (no hay entregas activas)
                    estado_pedido_pendiente = EstadoPedido.objects.get(nombre='Pendiente')
                    if self.pedido.estado_pedido.nombre != 'Pendiente':
                        self.pedido.estado_pedido = estado_pedido_pendiente
                        self.pedido.save()
                        print(f"✅ Pedido {self.pedido.codigo_pedido} actualizado a 'Pendiente' (caso por defecto)")
                        
            except EstadoPedido.DoesNotExist as e:
                print(f"⚠️ Estado de pedido no encontrado: {e}")
            
        else:
            raise ValidationError(f"No se puede restablecer una entrega en estado '{self.estado}'")