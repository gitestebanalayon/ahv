import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

class PedidoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("🔌 CONNECT - Aceptando conexión WebSocket")
        
        # Aceptar la conexión inmediatamente
        await self.accept()
        
        print("✅ CONNECT - Conexión aceptada")
        
        # Enviar mensaje de confirmación
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Conectado al WebSocket de pedidos',
            'timestamp': datetime.now().isoformat(),
            'status': 'connected'
        }))
        
        print("✅ CONNECT - Mensaje enviado")

    async def disconnect(self, close_code):
        print(f"🔌 DISCONNECT - Código: {close_code}")

    async def receive(self, text_data):
        print(f"📨 RECEIVE - Datos recibidos: {text_data[:100]}...")
        
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            print(f"📨 RECEIVE - Tipo de mensaje: {message_type}")
            
            if message_type == 'subscribe':
                print("📨 RECEIVE - Procesando suscripción")
                
                # Responder a la suscripción
                await self.send(text_data=json.dumps({
                    'type': 'subscribed',
                    'message': 'Suscrito correctamente',
                    'timestamp': datetime.now().isoformat()
                }))
                
                print("📨 RECEIVE - Respuesta de suscripción enviada")
                
            elif message_type == 'ping':
                print("📨 RECEIVE - Procesando ping")
                
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
                
            elif message_type == 'get_current_pedidos':
                print("📨 RECEIVE - Solicitando pedidos actuales")
                
                # Simular respuesta
                await self.send(text_data=json.dumps({
                    'type': 'current_pedidos',
                    'pedidos': [],
                    'count': 0,
                    'timestamp': datetime.now().isoformat()
                }))
                
            else:
                print(f"📨 RECEIVE - Mensaje no reconocido: {message_type}")
                
                await self.send(text_data=json.dumps({
                    'type': 'unknown_message',
                    'message': f'Tipo de mensaje no reconocido: {message_type}',
                    'timestamp': datetime.now().isoformat()
                }))
                
        except json.JSONDecodeError as e:
            print(f"❌ RECEIVE - Error JSON: {e}")
            
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Formato JSON inválido',
                'timestamp': datetime.now().isoformat()
            }))
            
        except Exception as e:
            print(f"❌ RECEIVE - Error inesperado: {e}")
            
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error interno: {str(e)}',
                'timestamp': datetime.now().isoformat()
            }))

    # Método para recibir mensajes del grupo (si usas channel_layer)
    async def pedido_created(self, event):
        print(f"📢 GROUP MESSAGE - pedido_created: {event}")
        
        try:
            await self.send(text_data=json.dumps({
                'type': 'pedido_created',
                'pedido': event.get('pedido', {}),
                'timestamp': datetime.now().isoformat(),
                'message': 'Nuevo pedido creado'
            }))
        except Exception as e:
            print(f"❌ GROUP MESSAGE - Error: {e}")