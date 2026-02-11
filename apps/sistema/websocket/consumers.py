# import json
# from channels.generic.websocket import AsyncWebsocketConsumer

# class PedidoConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # Extraemos el nombre del operativo de la URL
#         self.operativo_nombre = self.scope['url_route']['kwargs']['operativo_nombre']
#         # Creamos un nombre de grupo dinámico basado en el operativo
#         self.room_group_name = f"registro_{self.operativo_nombre}"

#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()

#     async def disconnect(self, code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def enviar_conteo(self, event):
#         await self.send(text_data=json.dumps({"total": event["conteo"]}))

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.core.serializers.json import DjangoJSONEncoder
from apps.sistema.models import Pedido
from apps.sistema.schemas.pedido import SchemaListarPedido

class PedidoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Nombre del grupo para todos los clientes admin
        self.room_group_name = 'pedidos_admin_group'
        
        # Unirse al grupo
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Enviar mensaje de confirmación
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Conectado al WebSocket de pedidos'
        }))

    async def disconnect(self, close_code):
        # Salir del grupo
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Recibir mensajes del WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        if message_type == 'subscribe':
            # Cliente se suscribe para recibir actualizaciones
            await self.send(text_data=json.dumps({
                'type': 'subscribed',
                'message': 'Suscrito a actualizaciones de pedidos'
            }))
        
        elif message_type == 'get_current_pedidos':
            # Enviar lista actual de pedidos
            pedidos = await self.get_pedidos_recent()
            await self.send(text_data=json.dumps({
                'type': 'current_pedidos',
                'pedidos': pedidos
            }))

    # Enviar actualización de nuevo pedido a todo el grupo
    async def pedido_created(self, event):
        pedido_data = event['pedido']
        
        await self.send(text_data=json.dumps({
            'type': 'pedido_created',
            'pedido': pedido_data,
            'message': 'Nuevo pedido creado'
        }))

    # Enviar actualización de pedido modificado
    async def pedido_updated(self, event):
        pedido_data = event['pedido']
        
        await self.send(text_data=json.dumps({
            'type': 'pedido_updated',
            'pedido': pedido_data,
            'message': 'Pedido actualizado'
        }))

    @database_sync_to_async
    def get_pedidos_recent(self):
        """Obtener los últimos 10 pedidos"""
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