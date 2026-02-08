# configuracion/pusher_service.py
import os
import pusher
from django.conf import settings
from datetime import datetime

class PusherService:
    """Servicio para manejar notificaciones con Pusher"""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Inicializar cliente Pusher"""
        print("🔧 Inicializando PusherService...")
        
        try:
            # Tus credenciales de Pusher - ¡VERIFICA QUE SON CORRECTAS!
            self.client = pusher.Pusher(
                app_id='2112607',
                key='7b9e25f3884835405cf2',
                secret='9e6bb489d228496d842f',
                cluster='mt1',
                ssl=True,
                timeout=5
            )
            self.active = True
            print("✅ PusherService: Configurado correctamente")
            
        except Exception as e:
            print(f"❌ Error inicializando Pusher: {e}")
            print("⚠️ Asegúrate de que 'pip install pusher' está instalado")
            self.client = None
            self.active = False
    
    def notify_pedido_created(self, pedido_data):
        """Notificar creación de nuevo pedido"""
        print(f"📡 Intentando enviar notificación para pedido: {pedido_data.get('codigo_pedido')}")
        
        if not self.active or not self.client:
            print("⚠️ Pusher no está activo, no se enviará notificación")
            return False
        
        try:
            # Enviar evento a Pusher
            self.client.trigger(
                'pedidos-channel',      # Canal
                'pedido-created',       # Evento
                {
                    'pedido': pedido_data,
                    'type': 'pedido_created',
                    'timestamp': datetime.now().isoformat()
                }
            )
            print(f"✅✅✅ EVENTO ENVIADO A PUSHER: pedido-created para {pedido_data.get('codigo_pedido')}")
            return True
            
        except Exception as e:
            print(f"❌❌❌ ERROR ENVIANDO A PUSHER: {type(e).__name__}: {e}")
            return False
    
    def notify_pedido_updated(self, pedido_data):
        """Notificar actualización de pedido"""
        if self.active and self.client:
            try:
                self.client.trigger(
                    'pedidos-channel',
                    'pedido-updated',
                    {'pedido': pedido_data}
                )
                return True
            except:
                pass
        return False

# Instancia global
pusher_service = PusherService()
print("✅ Módulo pusher_service cargado")