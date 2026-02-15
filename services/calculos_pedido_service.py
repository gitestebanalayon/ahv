# services/calculos_pedido_service.py
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q

class CalculosPedidoService:
    """
    Servicio que encapsula toda la lógica de cálculos de pedidos
    """
    
    def __init__(self, pedido):
        """
        Inicializa el servicio con un pedido
        """
        self.pedido = pedido
    
    def determinar_delivery(self):
        """Determina automáticamente el delivery según la cantidad de yardas"""
        from apps.administracion.models.hult_delivery import HultDelivery
        from apps.administracion.models.precio_hult_delivery import PrecioHultDelivery
        
        try:
            hult_delivery = HultDelivery.objects.filter(is_delete=False).order_by('yarda_minima')
            
            for hult in hult_delivery:
                if hult.verificar_rango_delivery(self.pedido.cantidad_yardas):
                    self.pedido.hultdelivery_id = hult.id

                    precio_activo = PrecioHultDelivery.objects.filter(
                        hult_delivery_id=hult.id,
                        is_active=True,
                    ).first()

                    return precio_activo.precio if precio_activo else None
            
        except Exception as e:
            print(f"Error al determinar hult: {e}")
        
        return None
    
    def obtener_precio_concreto_activo(self):
        """Obtiene el precio activo actual del tipo de concreto seleccionado"""
        from apps.administracion.models.tipo_concreto_precio import TipoConcretoPrecio
        
        try:
            precio_activo = TipoConcretoPrecio.objects.filter(
                tipo_concreto_id=self.pedido.tipo_concreto.id,
                is_active=True
            ).first()

            if precio_activo:
                self.pedido.precio_por_yarda_aplicado = precio_activo.precio
                self.pedido.precio_por_yarda_aplicado_codigo = precio_activo.codigo
            else:
                self.pedido.precio_por_yarda_aplicado = Decimal('0')
                self.pedido.precio_por_yarda_aplicado_codigo = None

            return precio_activo
            
        except Exception as e:
            print(f"Error obteniendo precio activo: {e}")
            return None
    
    def calcular_subtotal_agregados(self):
        """Calcula el subtotal de todos los agregados del pedido"""
        from apps.administracion.models.agregado_precio import AgregadoPrecio
        
        total = Decimal('0')
        try:
            fecha_referencia = self.pedido.fecha_creacion.date() if self.pedido.pk else timezone.now().date()
            
            agregados = self.pedido.agregado.all()
            
            for agregado in agregados:
                precio = AgregadoPrecio.objects.filter(
                    agregado=agregado,
                    fecha_inicio__lte=fecha_referencia,
                    is_active=True
                ).filter(
                    Q(fecha_fin__gte=fecha_referencia) | Q(fecha_fin__isnull=True)
                ).first()
                
                if precio:
                    subtotal_agregado = self.pedido.cantidad_yardas * precio.precio
                    total += subtotal_agregado
                
        except Exception as e:
            print(f"Error al calcular subtotal de agregados: {e}")
            import traceback
            traceback.print_exc()
        
        return total
    
    def calcular_todos_los_precios(self):
        """
        Calcula todos los precios del pedido de una vez
        """
        try:
            # 1. Determinar delivery
            precio_delivery = self.determinar_delivery()
            if precio_delivery:
                self.pedido.subtotal_hultdelivery = precio_delivery
            else:
                self.pedido.subtotal_hultdelivery = Decimal('0')
                self.pedido.hultdelivery = None

            # 2. Calcular precio del concreto
            self.obtener_precio_concreto_activo()

            if self.pedido.cantidad_yardas and self.pedido.precio_por_yarda_aplicado:
                self.pedido.subtotal_yardas = self.pedido.cantidad_yardas * self.pedido.precio_por_yarda_aplicado
            else:
                self.pedido.subtotal_yardas = Decimal('0')
            
            # 3. Calcular subtotal de agregados
            self.pedido.subtotal_agregados = self.calcular_subtotal_agregados()
            
            # 4. Calcular precio total
            self.pedido.precio_total = (
                (self.pedido.subtotal_yardas or Decimal('0')) + 
                (self.pedido.subtotal_agregados or Decimal('0')) + 
                (self.pedido.subtotal_hultdelivery or Decimal('0'))
            )
            
            return True
            
        except Exception as e:
            print(f"❌ Error al calcular precios: {e}")
            import traceback
            traceback.print_exc()
            
            self.pedido.subtotal_yardas = Decimal('0')
            self.pedido.subtotal_agregados = Decimal('0')
            self.pedido.precio_total = Decimal('0')
            
            return False