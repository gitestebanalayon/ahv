from ninja import Router, Query
from ninja_jwt.authentication import JWTAuth
from django.http import HttpRequest
from ninja.errors import HttpError
from django.core.exceptions import ValidationError
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from django.db import transaction
from typing import Dict, Any
from datetime import datetime
import os
import pusher  # ← NUEVO: Importar Pusher

from apps.sistema.models import Pedido, Entrega
from apps.cuenta.models import User
from apps.auxiliares.models import EstadoPedido
from apps.administracion.models import Agregado
from apps.sistema.schemas.pedido import SchemaListarPedido
from apps.schemas.list_response import ListResponse
from apps.schemas.types_messages import SuccessSchema, ErrorSchema
from apps.sistema.schemas.pedido import CrearPedidoSchema

from apps.decoradores.verificar_permisos import permission_required

tag = ['Pedido']
router = Router()


def get_pusher_client():
    """Obtener cliente Pusher (funciona en PythonAnywhere)"""
    try:
        # Detectar si estamos en PythonAnywhere
        is_pythonanywhere = 'pythonanywhere.com' in os.environ.get('SERVER_SOFTWARE', '')
        
        if is_pythonanywhere:
            # En producción: usar Pusher real
            client = pusher.Pusher(
                app_id=os.environ.get('PUSHER_APP_ID', ''),
                key=os.environ.get('PUSHER_KEY', ''),
                secret=os.environ.get('PUSHER_SECRET', ''),
                cluster=os.environ.get('PUSHER_CLUSTER', 'mt1'),  # ← Usa tu cluster
                ssl=True
            )
            print("✅ Pusher configurado para PythonAnywhere")
        else:
            # En desarrollo local: simular Pusher o usar Django Channels
            # Para desarrollo, puedes crear un mock o usar Channels
            client = None
            print("🔧 Desarrollo: Pusher en modo simulación")
            
        return client
        
    except Exception as e:
        print(f"⚠️ Error configurando Pusher: {e}")
        return None


@router.post("/crear", tags=tag, response={201: SuccessSchema, 400: ErrorSchema})
def crear_pedido(request, data: CrearPedidoSchema):
    """
    Crear nuevo pedido con notificación WebSocket vía Pusher
    """
    try:
        print(f"🎯 Datos recibidos: {data.dict()}")
        
        with transaction.atomic():
            # Validar que el cliente existe
            try:
                cliente = User.objects.get(id=data.cliente_id)
                print(f"✅ Cliente encontrado: {cliente.username}")
                
                if not cliente.is_customer:
                    return 400, ErrorSchema(
                        statusCode=400,
                        path=request.path,
                        message=f"El usuario {cliente.username} no es un cliente",
                        success=False,
                        timestamp=datetime.now().isoformat()
                    )
                    
                if not cliente.is_active:
                    return 400, ErrorSchema(
                        statusCode=400,
                        path=request.path,
                        message=f"El cliente {cliente.username} no está activo",
                        success=False,
                        timestamp=datetime.now().isoformat()
                    )
                    
            except User.DoesNotExist:
                return 400, ErrorSchema(
                    statusCode=400,
                    path=request.path,
                    message=f"Cliente ID {data.cliente_id} no encontrado",
                    success=False,
                    timestamp=datetime.now().isoformat()
                )
            
            # Obtener estado pendiente
            try:
                estado_pendiente = EstadoPedido.objects.get(nombre='pendiente')
            except EstadoPedido.DoesNotExist:
                return 400, ErrorSchema(
                    statusCode=400,
                    path=request.path,
                    message="Estado 'pendiente' no configurado en el sistema",
                    success=False,
                    timestamp=datetime.now().isoformat()
                )
            
            # Crear pedido
            pedido = Pedido(
                cliente=cliente,
                cantidad_yardas=data.cantidad_yardas,
                direccion_entrega=data.direccion_entrega,
                fecha_entrega=data.fecha_entrega,
                hora_entrega=data.hora_entrega,
                nota=data.nota or '',
                slump=data.slump,
                estado_pedido=estado_pendiente
            )
            
            # Guardar primero para obtener ID
            pedido.save()
            print(f"✅ Pedido guardado: {pedido.codigo_pedido} (ID: {pedido.id})")
            
            # Procesar agregados si existen
            if data.agregados and isinstance(data.agregados, list):
                agregados_instances = Agregado.objects.filter(id__in=data.agregados, is_delete=False)
                if agregados_instances.exists():
                    pedido.agregado.set(agregados_instances)
                    print(f"✅ Agregados asignados: {agregados_instances.count()}")
            
            # Calcular precios
            try:
                pedido.calcular_precios()
                
                # Actualizar campos calculados
                update_fields = [
                    'subtotal_yardas', 'subtotal_agregados', 'precio_total',
                    'rango_pedido', 'rango_pedido_codigo',
                    'precio_por_yarda_aplicado', 'precio_por_yarda_aplicado_codigo',
                    'fecha_modificacion'
                ]
                
                campos_existentes = [campo for campo in update_fields if hasattr(pedido, campo)]
                if campos_existentes:
                    pedido.save(update_fields=campos_existentes)
                    
            except Exception as e:
                print(f"⚠️ Error calculando precios: {e}")
                # Continuar aunque falle el cálculo
            
            # 🔥 NUEVO: Enviar notificación WebSocket VÍA PUSHER
            try:
                # Obtener cliente Pusher
                from configuracion.pusher_service import pusher_service
                
                # Preparar datos del pedido
                pedido_data = {
                    'id': pedido.id,
                    'codigo_pedido': pedido.codigo_pedido,
                    'cliente': cliente.nombre_apellido if hasattr(cliente, 'nombre_apellido') else cliente.username,
                    'cantidad_yardas': float(pedido.cantidad_yardas) if pedido.cantidad_yardas else 0,
                    'estado_pedido': str(pedido.estado_pedido),
                    'fecha_creacion': pedido.fecha_creacion.isoformat() if pedido.fecha_creacion else None,
                    'entregas': 0,
                    'precio_total': float(pedido.precio_total) if pedido.precio_total else 0,
                    'is_new': True,
                    'timestamp': datetime.now().isoformat()
                }
                
                if pusher_service:
                    
                    # Enviar notificación
                    websocket_sent = pusher_service.notify_pedido_created(pedido_data)
                    print(f"📡 Notificación WebSocket: {'ENVIADA' if websocket_sent else 'NO ENVIADA'}")
                    
                else:
                    # Fallback para desarrollo local: usar Django Channels
                    try:
                        from channels.layers import get_channel_layer
                        from asgiref.sync import async_to_sync
                        
                        channel_layer = get_channel_layer()
                        async_to_sync(channel_layer.group_send)(
                            'pedidos_admin_group',
                            {
                                'type': 'pedido_created',
                                'pedido': pedido_data
                            }
                        )
                        print(f"📡 Channels local: Notificación enviada para {pedido.codigo_pedido}")
                    except ImportError:
                        print("⚠️ Channels no disponible en desarrollo")
                
            except Exception as ws_error:
                print(f"⚠️ Error enviando notificación: {ws_error}")
                # No fallar la creación del pedido por error en WebSocket
            
            return 201, SuccessSchema(
                statusCode=201,
                path=request.path,
                message=f"Pedido {pedido.codigo_pedido} creado exitosamente",
                success=True,
                timestamp=datetime.now().isoformat(),
                data={
                    "pedido_id": pedido.id,
                    "codigo_pedido": pedido.codigo_pedido,
                    "precio_total": float(pedido.precio_total) if pedido.precio_total else 0,
                    "websocket_sent": websocket_sent if 'websocket_sent' in locals() else False
                }
            )
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        
        # CORREGIDO: Devolver error correctamente
        return 400, ErrorSchema(
            statusCode=400,
            path=request.path,
            message=f"Error interno: {str(e)}",
            success=False,
            timestamp=datetime.now().isoformat()
        )
    
# @permission_required('sistema.view_conductor')
@router.get("/listar", tags=tag, response=ListResponse)
def listar(
    request: HttpRequest,
    page: int = Query(1, description="Número de página"),
    page_size: int = Query(10, description="Cantidad de elementos por página"),
    pedido_id: int = Query(None, description="Filtrar por ID el pedido"),
):
    # Validar y ajustar parámetros de paginación
    page = max(1, page)
    page_size = min(max(1, page_size), 100)

    # Query base con prefetch_related para optimizar las consultas
    qs = Pedido.objects.all().order_by('id')
    
    # Filtrar por pedido_id si se proporciona
    if pedido_id:
        qs = qs.filter(id=pedido_id)
    
    # IMPORTANTE: Prefetch las entregas relacionadas para optimizar
    # Django usa 'entrega_set' por defecto cuando no hay related_name
    qs = qs.prefetch_related('entrega_set')
    
    # Calcular totales
    total_data = qs.count()
    total_pages = (total_data + page_size - 1) // page_size

    # Aplicar paginación
    start = (page - 1) * page_size
    end = start + page_size
    page_items = list(qs[start:end])

    # Serializar los datos
    items = [SchemaListarPedido.from_orm(item) for item in page_items]

    return {
        "data": items,
        "totalData": total_data,
        "totalPages": total_pages,
        "currentPage": page
    }