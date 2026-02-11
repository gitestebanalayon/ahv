from ninja import Router, Query
from ninja_jwt.authentication import JWTAuth
from django.http import HttpRequest
from ninja.errors import HttpError
from django.core.exceptions import ValidationError
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from django.db import transaction
from typing import Dict, Any
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from datetime import datetime
from decouple import config
import jwt

from apps.sistema.models import Pedido, Entrega
from apps.cuenta.models import User
from apps.auxiliares.models import EstadoPedido
from apps.administracion.models import Agregado
from apps.sistema.schemas.pedido import  SchemaListarPedido
from apps.schemas.list_response import ListResponse
from apps.schemas.types_messages import SuccessSchema, ErrorSchema
from apps.sistema.schemas.pedido import CrearPedidoSchema

from apps.decoradores.verificar_permisos import permission_required

tag = ['Pedido']
router = Router()

@permission_required('sistema.add_pedido')
@router.post("/crear", tags=tag, response={201: SuccessSchema, 400: ErrorSchema}, auth=JWTAuth())
def crear_pedido(request, data: CrearPedidoSchema):
    """
    Crear nuevo pedido con notificación WebSocket
    """
    try:
        print(f"🎯 Datos recibidos: {data.dict()}")
        
        with transaction.atomic():
            # Validar que el cliente existe
            try:
                cliente = User.objects.get(id=data.cliente_id)
                print(f"✅ Cliente encontrado: {cliente.username}")
                
                if not cliente.is_customer:
                    return 400, ErrorSchema.from_exception(
                        status_code=400,
                        path=request.path,
                        message=f"El usuario {cliente.username} no es un cliente"
                    )
                    
                if not cliente.is_active:
                    return 400, ErrorSchema.from_exception(
                        status_code=400,
                        path=request.path,
                        message=f"El cliente {cliente.username} no está activo"
                    )
                    
            except User.DoesNotExist:
                return 400, ErrorSchema.from_exception(
                    status_code=400,
                    path=request.path,
                    message=f"Cliente ID {data.cliente_id} no encontrado"
                )
            

             # ✅ SOLUCIÓN: Obtener la instancia de TipoConcreto
            try:
                from apps.administracion.models.tipo_concreto import TipoConcreto  # Importa aquí o arriba
                tipo_concreto = TipoConcreto.objects.get(id=data.tipo_concreto_id)
            except TipoConcreto.DoesNotExist:
                return 400, ErrorSchema.from_exception(
                    status_code=400,
                    path=request.path,
                    message=f"Tipo de concreto ID {data.tipo_concreto_id} no encontrado"
                )
            
            # Obtener estado pendiente
            try:
                estado_pendiente = EstadoPedido.objects.get(nombre='Pendiente')
            except EstadoPedido.DoesNotExist:
                return 400, ErrorSchema.from_exception(
                    status_code=400,
                    path=request.path,
                    message="Estado 'pendiente' no configurado en el sistema"
                )
            
            # Crear pedido
            pedido = Pedido(
                cliente=cliente,
                tipo_concreto=tipo_concreto,
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
            
            # ============= 🔴 CORRECCIÓN HULTDELIVERY =============
            try:
                # 1. Determinar el HultDelivery según yardas
                from apps.administracion.models.hult_delivery import HultDelivery
                from apps.administracion.models.precio_hult_delivery import PrecioHultDelivery
                
                hult_delivery = HultDelivery.objects.filter(is_delete=False).order_by('yarda_minima')
                
                for hult in hult_delivery:
                    if hult.verificar_rango_delivery(pedido.cantidad_yardas):
                        # Asignar el hultdelivery al pedido
                        pedido.hultdelivery = hult
                        
                        # Obtener precio activo
                        precio_activo = PrecioHultDelivery.objects.filter(
                            hult_delivery=hult,
                            is_active=True
                        ).first()
                        
                        if precio_activo:
                            pedido.subtotal_hultdelivery = precio_activo.precio
                            print(f"✅ HultDelivery asignado: {hult.nombre} - ${precio_activo.precio}")
                        else:
                            pedido.subtotal_hultdelivery = 0
                            print(f"⚠️ HultDelivery {hult.nombre} sin precio activo")
                        
                        break
                
                # Guardar los cambios de hultdelivery
                pedido.save(update_fields=['hultdelivery', 'subtotal_hultdelivery', 'fecha_modificacion'])
                
            except Exception as e:
                print(f"⚠️ Error asignando HultDelivery: {e}")
                import traceback
                traceback.print_exc()
            # ======================================================


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
            
            # Enviar notificación WebSocket
            try:
                channel_layer = get_channel_layer()
                pedido_data = {
                    'id': pedido.id,
                    'codigo_pedido': pedido.codigo_pedido,
                    'cliente': cliente.nombre_apellido if hasattr(cliente, 'nombre_apellido') else cliente.username,
                    'cantidad_yardas': float(pedido.cantidad_yardas) if pedido.cantidad_yardas else 0,
                    'estado_pedido': str(pedido.estado_pedido),
                    'fecha_creacion': pedido.fecha_creacion.isoformat() if pedido.fecha_creacion else None,
                    'entregas': 0,
                    'precio_total': float(pedido.precio_total) if pedido.precio_total else 0,
                    'is_new': True
                }
                
                async_to_sync(channel_layer.group_send)(
                    'pedidos_admin_group',
                    {
                        'type': 'pedido_created',
                        'pedido': pedido_data
                    }
                )
                print(f"📡 WebSocket enviado para {pedido.codigo_pedido}")
                
            except Exception as ws_error:
                print(f"⚠️ Error WebSocket: {ws_error}")
            
            return 201, SuccessSchema.from_success(
                status_code=201,
                path=request.path,
                message=f"Pedido {pedido.codigo_pedido} creado exitosamente",
                data={
                    "pedido_id": pedido.id,
                    "codigo_pedido": pedido.codigo_pedido,
                    "precio_total": float(pedido.precio_total) if pedido.precio_total else 0,
                    "cliente": cliente.username
                }
            )
            
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
        # Para errores también devuelve tupla
        return 400, ErrorSchema.from_exception(
            status_code=400,
            path=request.path,
            message=f"Error interno: {str(e)}"
        )
    
@permission_required('sistema.view_pedido')
@router.get("/listar", tags=tag, response=ListResponse, auth=JWTAuth())
def listar(
    request: HttpRequest,
    page: int = Query(1, description="Número de página"),
    page_size: int = Query(10, description="Cantidad de elementos por página"),
    pedido_id: int = Query(None, description="Filtrar por ID el pedido"),
):
    user = request.user


    # Validar y ajustar parámetros de paginación
    page = max(1, page)
    page_size = min(max(1, page_size), 100)

    # Query base
    qs = Pedido.objects.all().order_by('-fecha_creacion')  # Orden descendente
    
    # 🔥 FILTROS SEGÚN ROL
    es_cliente = user.groups.filter(name='Clientes').exists()
    es_administrador = user.is_staff or user.groups.filter(name='Administradores').exists()
    
    if es_cliente:
        # Clientes: solo ven sus propios pedidos
        qs = qs.filter(cliente=user)
    elif es_administrador:
        # Administradores: pueden ver todo
        pass
    else:
        # Otros roles: lógica personalizada
        pass
    
    # Filtrar por pedido_id si se proporciona
    if pedido_id:
        qs = qs.filter(id=pedido_id)
    
    # IMPORTANTE: Prefetch las entregas relacionadas para optimizar
    # Django usa 'entrega_set' por defecto cuando no hay related_name
     # Optimizar consultas
    qs = qs.select_related('cliente', 'estado_pedido', 'tipo_concreto')\
            .prefetch_related('entrega_set', 'agregado')
    
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