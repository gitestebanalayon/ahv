from ninja import Router, Query
from ninja_jwt.authentication import JWTAuth
from django.http import HttpRequest
from ninja.errors import HttpError
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat

from apps.sistema.models import Pedido, Entrega
from apps.sistema.schemas.pedido import  SchemaListarPedido
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