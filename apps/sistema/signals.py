# apps/sistema/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from configuracion.pusher_backend import pusher_backend
from .models import Pedido

@receiver(post_save, sender=Pedido)
def notify_pedido_change(sender, instance, created, **kwargs):
    """Notificar cuando un pedido se crea o actualiza"""
    
    # Serializar el pedido
    pedido_data = {
        'id': instance.id,
        'codigo_pedido': instance.codigo_pedido,
        'cliente': instance.cliente.nombre_apellido if instance.cliente else 'Sin cliente',
        'cantidad_yardas': float(instance.cantidad_yardas) if instance.cantidad_yardas else 0,
        'precio_total': float(instance.precio_total) if instance.precio_total else 0,
        'estado': str(instance.estado_pedido),
        'fecha_creacion': instance.fecha_creacion.isoformat() if instance.fecha_creacion else None,
        'accion': 'creado' if created else 'actualizado'
    }
    
    # Enviar notificación
    if created:
        pusher_backend.send_pedido_created(pedido_data)
    else:
        pusher_backend.send_pedido_updated(pedido_data)

@receiver(post_delete, sender=Pedido)
def notify_pedido_deleted(sender, instance, **kwargs):
    """Notificar cuando un pedido se elimina"""
    pusher_backend.send_pedido_deleted({
        'id': instance.id,
        'codigo_pedido': instance.codigo_pedido,
        'accion': 'eliminado'
    })