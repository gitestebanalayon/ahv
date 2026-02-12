# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from channels.layers import get_channel_layer
# from asgiref.sync import async_to_sync
# from .models import Pedido

# @receiver(post_save, sender=Pedido)
# def pedido_created_signal(sender, instance, created, **kwargs):
#     """
#     Señal que se dispara cuando se crea o actualiza un pedido.
#     Envía notificación a través de WebSocket.
#     """
#     if not created:  # Solo para actualizaciones, las creaciones se manejan en la API
#         return
    
#     try:
#         channel_layer = get_channel_layer()
        
#         # Preparar datos del pedido
#         pedido_data = {
#             'id': instance.id,
#             'codigo_pedido': instance.codigo_pedido,
#             'cliente': instance.cliente.nombre_apellido if instance.cliente else '',
#             'cantidad_yardas': float(instance.cantidad_yardas) if instance.cantidad_yardas else 0,
#             'estado_pedido': str(instance.estado_pedido),
#             'fecha_creacion': instance.fecha_creacion.isoformat() if instance.fecha_creacion else None,
#             'entregas': instance.entrega_set.count(),
#             'precio_total': float(instance.precio_total) if instance.precio_total else 0,
#         }
        
#         # Enviar al grupo
#         async_to_sync(channel_layer.group_send)(
#             'pedidos_admin_group',
#             {
#                 'type': 'pedido_created',
#                 'pedido': pedido_data
#             }
#         )
        
#         print(f"📡 Señal WebSocket enviada para pedido {instance.codigo_pedido}")
        
#     except Exception as e:
#         print(f"❌ Error en señal WebSocket: {e}")