from ninja import Router, Query
from ninja_jwt.authentication import JWTAuth
from django.http import HttpRequest
from ninja.errors import HttpError
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from typing import List

from apps.sistema.models import Pedido, Entrega
from apps.sistema.schemas.pedido import  SchemaListarPedido, EntregaActionResponse, EntregaActionRequest

from apps.schemas.list_response import ListResponse
from apps.schemas.types_messages import SuccessSchema, ErrorSchema

from apps.decoradores.verificar_permisos import permission_required

tag = ['Pedido']
router = Router()


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
    
    
    
    
    
    
    
    
# Vista para marcar entrega como iniciada
@permission_required('sistema.change_entrega')
@router.post("/entregas/{entrega_id}/iniciar", tags=tag, response={200: EntregaActionResponse, 400: ErrorSchema})
def iniciar_entrega(
    request: HttpRequest,
    entrega_id: int
):
    """
    Marca una entrega como "En Camino"
    """
    try:
        entrega = Entrega.objects.get(id=entrega_id)
        
        # Verificar permisos adicionales
        if not request.user.has_perm('sistema.change_entrega'):
            return 403, {"message": "No tiene permiso para realizar esta acción"}
        
        if entrega.estado == 'programado':
            entrega.marcar_como_iniciado()
            
            return 200, {
                "success": True,
                "message": f"Entrega {entrega.codigo_entrega} marcada como 'En Camino'",
                "estado": entrega.estado,
                "fecha_hora_salida": entrega.fecha_hora_salida,
                "conductor_disponible": False,  # En viaje
                "vehiculo_disponible": False    # En viaje
            }
        else:
            return 400, {
                "message": f"No se puede iniciar una entrega en estado '{entrega.get_estado_display()}'"
            }
            
    except Entrega.DoesNotExist:
        return 404, {"message": "Entrega no encontrada"}
    except Exception as e:
        return 500, {"message": f"Error al iniciar la entrega: {str(e)}"}

# Vista para marcar entrega como completada
@permission_required('sistema.change_entrega')
@router.post("/entregas/{entrega_id}/completar", tags=tag, response={200: EntregaActionResponse, 400: ErrorSchema})
def completar_entrega(
    request: HttpRequest,
    entrega_id: int
):
    """
    Marca una entrega como "Entregada" y libera recursos
    """
    try:
        entrega = Entrega.objects.get(id=entrega_id)
        
        # Verificar permisos adicionales
        if not request.user.has_perm('sistema.change_entrega'):
            return 403, {"message": "No tiene permiso para realizar esta acción"}
        
        if entrega.estado in ['programado', 'en_camino']:
            entrega.marcar_como_completado()
            
            return 200, {
                "success": True,
                "message": f"Entrega {entrega.codigo_entrega} completada exitosamente",
                "estado": entrega.estado,
                "fecha_hora_entrega": entrega.fecha_hora_entrega,
                "conductor_disponible": entrega.conductor.estado_conductor_nombre.nombre == 'Disponible',
                "vehiculo_disponible": entrega.vehiculo.estado_vehiculo_nombre.nombre == 'Disponible',
                "pedido_estado": entrega.pedido.estado_pedido.nombre if entrega.pedido.estado_pedido else None
            }
        else:
            return 400, {
                "message": f"No se puede completar una entrega en estado '{entrega.get_estado_display()}'"
            }
            
    except Entrega.DoesNotExist:
        return 404, {"message": "Entrega no encontrada"}
    except Exception as e:
        return 500, {"message": f"Error al completar la entrega: {str(e)}"}

# Vista para cancelar una entrega
@permission_required('sistema.change_entrega')
@router.post("/entregas/{entrega_id}/cancelar", tags=tag, response={200: EntregaActionResponse, 400: ErrorSchema})
def cancelar_entrega(
    request: HttpRequest,
    entrega_id: int,
    payload: EntregaActionRequest
):
    """
    Cancela una entrega y libera recursos
    """
    try:
        entrega = Entrega.objects.get(id=entrega_id)
        
        # Verificar permisos adicionales
        if not request.user.has_perm('sistema.change_entrega'):
            return 403, {"message": "No tiene permiso para realizar esta acción"}
        
        if entrega.estado in ['programado', 'en_camino']:
            # Guardar motivo si se proporciona
            if payload.motivo:
                entrega.nota = f"CANCELADA - Motivo: {payload.motivo}\n{entrega.nota or ''}"
            
            entrega.cancelar()
            
            return 200, {
                "success": True,
                "message": f"Entrega {entrega.codigo_entrega} cancelada" + 
                          (f" - Motivo: {payload.motivo}" if payload.motivo else ""),
                "estado": entrega.estado,
                "conductor_disponible": entrega.conductor.estado_conductor_nombre.nombre == 'Disponible',
                "vehiculo_disponible": entrega.vehiculo.estado_vehiculo_nombre.nombre == 'Disponible'
            }
        else:
            return 400, {
                "message": f"No se puede cancelar una entrega en estado '{entrega.get_estado_display()}'"
            }
            
    except Entrega.DoesNotExist:
        return 404, {"message": "Entrega no encontrada"}
    except Exception as e:
        return 500, {"message": f"Error al cancelar la entrega: {str(e)}"}

# Vista para obtener estado de una entrega específica
@permission_required('sistema.view_entrega')
@router.get("/entregas/{entrega_id}/estado", tags=tag, response={200: EntregaActionResponse, 404: ErrorSchema})
def obtener_estado_entrega(
    request: HttpRequest,
    entrega_id: int
):
    """
    Obtiene el estado actual de una entrega
    """
    try:
        entrega = Entrega.objects.get(id=entrega_id)
        
        return 200, {
            "success": True,
            "estado": entrega.estado,
            "estado_display": entrega.get_estado_display(),
            "fecha_hora_salida": entrega.fecha_hora_salida,
            "fecha_hora_entrega": entrega.fecha_hora_entrega,
            "entregado": entrega.entregado,
            "conductor": {
                "id": entrega.conductor.id,
                "nombre": entrega.conductor.nombre,
                "estado": entrega.conductor.estado_conductor_nombre.nombre
            },
            "vehiculo": {
                "id": entrega.vehiculo.id,
                "alias": entrega.vehiculo.alias,
                "estado": entrega.vehiculo.estado_vehiculo_nombre.nombre
            },
            "pedido": {
                "codigo": entrega.pedido.codigo_pedido,
                "estado": entrega.pedido.estado_pedido.nombre if entrega.pedido.estado_pedido else None
            }
        }
            
    except Entrega.DoesNotExist:
        return 404, {"message": "Entrega no encontrada"}

# Vista para listar entregas de un pedido específico
@permission_required('sistema.view_pedido')
@router.get("/{pedido_id}/entregas", tags=tag, response={200: List[SchemaListarPedido], 404: ErrorSchema})
def listar_entregas_pedido(
    request: HttpRequest,
    pedido_id: int
):
    """
    Lista todas las entregas de un pedido específico
    """
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        entregas = pedido.entrega_set.all().order_by('secuencia')
        
        # Podrías crear un schema específico para entregas si lo necesitas
        # Por ahora usamos el mismo schema de pedido
        
        return 200, [
            {
                "id": e.id,
                "codigo_entrega": e.codigo_entrega,
                "secuencia": e.secuencia,
                "conductor": e.conductor.nombre,
                "vehiculo": e.vehiculo.alias,
                "yardas_asignadas": float(e.yardas_asignadas),
                "estado": e.estado,
                "estado_display": e.get_estado_display(),
                "fecha_hora_salida": e.fecha_hora_salida,
                "fecha_hora_entrega": e.fecha_hora_entrega,
                "entregado": e.entregado
            }
            for e in entregas
        ]
            
    except Pedido.DoesNotExist:
        return 404, {"message": "Pedido no encontrado"}

# Vista para verificar si todas las entregas de un pedido están completas
@permission_required('sistema.view_pedido')
@router.get("/{pedido_id}/verificar-completado", tags=tag, response={200: dict, 404: ErrorSchema})
def verificar_pedido_completado(
    request: HttpRequest,
    pedido_id: int
):
    """
    Verifica si todas las entregas de un pedido están completas
    """
    try:
        pedido = Pedido.objects.get(id=pedido_id)
        
        entregas_totales = pedido.entrega_set.count()
        entregas_completadas = pedido.entrega_set.filter(entregado=True).count()
        entregas_pendientes = pedido.entrega_set.filter(entregado=False).count()
        
        return 200, {
            "pedido_id": pedido.id,
            "codigo_pedido": pedido.codigo_pedido,
            "total_entregas": entregas_totales,
            "entregas_completadas": entregas_completadas,
            "entregas_pendientes": entregas_pendientes,
            "completado": entregas_pendientes == 0,
            "porcentaje_completado": (entregas_completadas / entregas_totales * 100) if entregas_totales > 0 else 0
        }
            
    except Pedido.DoesNotExist:
        return 404, {"message": "Pedido no encontrada"}