import json
from channels.generic.websocket import AsyncWebsocketConsumer

class PedidoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Aceptar la conexión sin unir a grupo
        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Conectado al WebSocket de pedidos'
        }))

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        pass