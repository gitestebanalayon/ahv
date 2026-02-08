# configuracion/pusher_backend.py
import os
from django.conf import settings
import pusher

class PusherBackend:
    """Manejador de WebSockets usando Pusher"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializar cliente Pusher"""
        self.is_production = hasattr(settings, 'IS_PYTHONANYWHERE') and settings.IS_PYTHONANYWHERE
        
        if self.is_production:
            try:
                self.client = pusher.Pusher(
                    app_id=os.environ.get('PUSHER_APP_ID', ''),
                    key=os.environ.get('PUSHER_KEY', ''),
                    secret=os.environ.get('PUSHER_SECRET', ''),
                    cluster=os.environ.get('PUSHER_CLUSTER', 'us2'),
                    ssl=True,
                    timeout=5
                )
                print("✅ Pusher inicializado para producción")
            except Exception as e:
                print(f"❌ Error inicializando Pusher: {e}")
                self.client = None
        else:
            # En desarrollo, podemos simular Pusher o usar un mock
            self.client = None
            print("🔧 Desarrollo: Pusher en modo simulación")
    
    def send_pedido_created(self, pedido_data):
        """Enviar notificación de nuevo pedido"""
        if not self.is_production:
            # En desarrollo, usar Channels local
            return self._send_via_channels(pedido_data)
        
        if self.client is None:
            print("⚠️ Pusher no configurado")
            return False
        
        try:
            self.client.trigger(
                'pedidos-channel',      # Nombre del canal
                'pedido-created',       # Nombre del evento
                {
                    'pedido': pedido_data,
                    'type': 'pedido_created',
                    'timestamp': self._get_timestamp()
                }
            )
            print(f"✅ Evento enviado a Pusher: {pedido_data.get('codigo_pedido', 'N/A')}")
            return True
        except Exception as e:
            print(f"❌ Error enviando a Pusher: {e}")
            return False
    
    def send_pedido_updated(self, pedido_data):
        """Enviar notificación de pedido actualizado"""
        if self.client and self.is_production:
            try:
                self.client.trigger(
                    'pedidos-channel',
                    'pedido-updated',
                    {
                        'pedido': pedido_data,
                        'type': 'pedido_updated',
                        'timestamp': self._get_timestamp()
                    }
                )
                return True
            except Exception as e:
                print(f"Error enviando actualización: {e}")
        return False
    
    def _send_via_channels(self, pedido_data):
        """Para desarrollo local: usar Django Channels"""
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                'pedidos_admin_group',
                {
                    'type': 'pedido_created',
                    'pedido': pedido_data
                }
            )
            return True
        except Exception as e:
            print(f"Error usando Channels: {e}")
            return False
    
    def _get_timestamp(self):
        """Obtener timestamp actual"""
        import time
        return int(time.time() * 1000)

# Instancia global
pusher_backend = PusherBackend()