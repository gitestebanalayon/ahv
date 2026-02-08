import json
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers.json import DjangoJSONEncoder
from apps.sistema.models import Pedido
from apps.sistema.schemas.pedido import SchemaListarPedido
from django.conf import settings
import time

class PedidoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"🔗 Intentando conectar WebSocket desde: {self.scope['client']}")
        
        # IMPORTANTE: Para PythonAnywhere, necesitamos aceptar todas las conexiones
        # ya que PythonAnywhere maneja el proxy inverso
        if not settings.DEBUG:
            # En producción (PythonAnywhere), verificar origen
            origin = self.scope.get('headers', {}).get(b'origin', b'').decode()
            if origin and not origin.startswith('https://ahv.pythonanywhere.com'):
                print(f"❌ Origen no permitido en producción: {origin}")
                await self.close(code=4003)
                return
        
        # Nombre del grupo para todos los clientes admin
        self.room_group_name = 'pedidos_admin_group'
        
        try:
            # Unirse al grupo
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            
            # Aceptar la conexión ANTES de enviar mensajes
            await self.accept()
            
            print(f"✅ WebSocket conectado exitosamente")
            
            # Enviar mensaje de confirmación
            await self.send(text_data=json.dumps({
                'type': 'connection_established',
                'message': 'Conectado al WebSocket de pedidos',
                'timestamp': time.time()
            }))
            
            # Iniciar tarea de keep-alive para PythonAnywhere
            if not settings.DEBUG:
                self.keep_alive_task = asyncio.create_task(self.send_keep_alive())
                
        except Exception as e:
            print(f"❌ Error en connect: {e}")
            # Si hay error, cerrar la conexión limpiamente
            try:
                await self.close(code=1011)
            except:
                pass

    async def disconnect(self, close_code):
        print(f"🔌 WebSocket desconectado, código: {close_code}")
        
        # Cancelar tarea de keep-alive si existe
        if hasattr(self, 'keep_alive_task'):
            self.keep_alive_task.cancel()
        
        # Salir del grupo
        try:
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )
        except:
            pass

    async def send_keep_alive(self):
        """Enviar mensajes de keep-alive periódicos para mantener conexión activa en PythonAnywhere"""
        while True:
            await asyncio.sleep(30)  # Cada 30 segundos
            try:
                await self.send(text_data=json.dumps({
                    'type': 'keep_alive',
                    'timestamp': time.time(),
                    'message': 'ping'
                }))
            except:
                break

    # Recibir mensajes del WebSocket
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            message_type = text_data_json.get('type')
            
            print(f"📥 Mensaje recibido: {message_type}")
            
            if message_type == 'subscribe':
                # Cliente se suscribe para recibir actualizaciones
                await self.send(text_data=json.dumps({
                    'type': 'subscribed',
                    'message': 'Suscrito a actualizaciones de pedidos',
                    'timestamp': time.time()
                }))
            
            elif message_type == 'get_current_pedidos':
                # Enviar lista actual de pedidos
                pedidos = await self.get_pedidos_recent()
                await self.send(text_data=json.dumps({
                    'type': 'current_pedidos',
                    'pedidos': pedidos,
                    'timestamp': time.time()
                }))
            
            elif message_type == 'pong':
                # Respuesta a keep_alive
                await self.send(text_data=json.dumps({
                    'type': 'pong_received',
                    'timestamp': time.time()
                }))
                
        except json.JSONDecodeError as e:
            print(f"❌ Error decodificando JSON: {e}")
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'JSON inválido'
            }))
        except Exception as e:
            print(f"❌ Error en receive: {e}")

    # Enviar actualización de nuevo pedido a todo el grupo
    async def pedido_created(self, event):
        try:
            pedido_data = event['pedido']
            
            await self.send(text_data=json.dumps({
                'type': 'pedido_created',
                'pedido': pedido_data,
                'message': 'Nuevo pedido creado',
                'timestamp': time.time()
            }))
            
            print(f"📦 Notificación de nuevo pedido enviada: {pedido_data.get('codigo_pedido', 'N/A')}")
            
        except Exception as e:
            print(f"❌ Error en pedido_created: {e}")

    # Enviar actualización de pedido modificado
    async def pedido_updated(self, event):
        try:
            pedido_data = event['pedido']
            
            await self.send(text_data=json.dumps({
                'type': 'pedido_updated',
                'pedido': pedido_data,
                'message': 'Pedido actualizado',
                'timestamp': time.time()
            }))
            
        except Exception as e:
            print(f"❌ Error en pedido_updated: {e}")

    @database_sync_to_async
    def get_pedidos_recent(self):
        """Obtener los últimos 10 pedidos"""
        try:
            pedidos = Pedido.objects.all().order_by('-fecha_creacion')[:10]
            result = []
            
            for pedido in pedidos:
                # Serializar el pedido
                schema = SchemaListarPedido.from_orm(pedido)
                result.append({
                    'id': pedido.id,
                    'codigo_pedido': pedido.codigo_pedido,
                    'cliente': pedido.cliente.nombre_apellido if pedido.cliente else '',
                    'cantidad_yardas': float(pedido.cantidad_yardas) if pedido.cantidad_yardas else 0,
                    'estado_pedido': str(pedido.estado_pedido),
                    'fecha_creacion': pedido.fecha_creacion.isoformat() if pedido.fecha_creacion else None,
                    'entregas': len(pedido.entrega_set.all()),
                    'precio_total': float(pedido.precio_total) if pedido.precio_total else 0,
                })
            
            return result
        except Exception as e:
            print(f"❌ Error en get_pedidos_recent: {e}")
            return []