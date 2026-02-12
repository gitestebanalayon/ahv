# apps/administracion/api/tipo_concreto.py
from ninja import Router, Query
from ninja_jwt.authentication import JWTAuth
from django.http import HttpRequest
from ninja.errors import HttpError
from django.db.models import Q, Value, CharField, OuterRef, Subquery, DecimalField
from django.db.models.functions import Concat, Coalesce
from decimal import Decimal
from datetime import date

from apps.administracion.models.tipo_concreto import TipoConcreto
from apps.administracion.models.tipo_concreto_precio import TipoConcretoPrecio
from apps.administracion.models.hult_delivery import HultDelivery
from apps.administracion.models.precio_hult_delivery import PrecioHultDelivery
from apps.administracion.models.agregado import Agregado
from apps.administracion.models.agregado_precio import AgregadoPrecio

from apps.administracion.schemas.tipo_concreto import SchemaCrear, SchemaListar
from apps.schemas.list_response import ListResponse
from apps.schemas.types_messages import SuccessSchema, ErrorSchema

from apps.decoradores.verificar_permisos import permission_required

tag = ['Precios']
router = Router()

@router.get("tipo_concreto/precios", tags=tag, response=ListResponse, auth=JWTAuth())
@permission_required('administracion.view_tipoconcreto')
def tipo_concreto_precios(
    request: HttpRequest,
    page: int = Query(1, description="Número de página"),
    page_size: int = Query(10, description="Cantidad de elementos por página"),
    all: str = Query(None, description="Búsqueda general en todos los campos"),
    tipo_concreto_id: int = Query(None, description="Filtrar por ID de tipo de periodo"),
    nombre: str = Query(None, description="Filtrar por nombre"),
    descripcion: str = Query(None, description="Filtrar por descripción")
):
    # Validar y ajustar parámetros de paginación
    page = max(1, page)
    page_size = min(max(1, page_size), 100)

    # Subquery para obtener el precio actual - NOMBRE DIFERENTE al property
    precio_actual_subquery = TipoConcretoPrecio.objects.filter(
        tipo_concreto=OuterRef('pk'),
        is_active=True,
        fecha_inicio__lte=date.today()
    ).order_by('-fecha_inicio').values('precio')[:1]
    
    # Query base con anotaciones - usando prefijo para evitar conflicto
    qs = TipoConcreto.objects.filter(
        is_delete=False
    ).annotate(
        _precio_actual=Coalesce(
            Subquery(precio_actual_subquery, output_field=DecimalField()),
            Value(Decimal('0.00'))
        )
    ).order_by('id')

    if all:
        # Buscar frase completa en campos concatenados
        qs_concat = qs.annotate(
            busqueda_completa=Concat(
                'nombre', 
                Value(' '), 
                'descripcion',
                'codigo',
                output_field=CharField()
            )
        ).filter(busqueda_completa__icontains=all)
        
        qs = qs.filter(
            Q(pk__in=qs_concat.values('pk'))
        ).distinct()
    
    # Filtros específicos
    if tipo_concreto_id:
        qs = qs.filter(id=tipo_concreto_id)
    
    if nombre:
        qs = qs.filter(nombre__icontains=nombre)
    
    if descripcion:
        qs = qs.filter(descripcion__icontains=descripcion)

    # Calcular totales
    total_data = qs.count()
    total_pages = (total_data + page_size - 1) // page_size

    # Aplicar paginación
    start = (page - 1) * page_size
    end = start + page_size
    page_items = list(qs[start:end])

    # Serializar los datos - usar el valor anotado
    items = []
    for item in page_items:
        items.append({
            "id": item.id,
            "codigo": item.codigo,
            "nombre": item.nombre,
            "descripcion": item.descripcion,
            "precio_actual": getattr(item, '_precio_actual', 0)  # Usar el campo anotado
        })

    return {
        "data": items,
        "totalData": total_data,
        "totalPages": total_pages,
        "currentPage": page
    }
    
    
@router.get("hult_delivery/precios", tags=tag, response=ListResponse, auth=JWTAuth())
@permission_required('administracion.view_hultdelivery')
def hult_delivery_precios(
    request: HttpRequest,
    page: int = Query(1, description="Número de página"),
    page_size: int = Query(10, description="Cantidad de elementos por página"),
    all: str = Query(None, description="Búsqueda general en todos los campos"),
    agregado_id: int = Query(None, description="Filtrar por ID de hult delivery"),
    nombre: str = Query(None, description="Filtrar por nombre"),
):
    # Validar y ajustar parámetros de paginación
    page = max(1, page)
    page_size = min(max(1, page_size), 100)

    # Subquery para obtener el precio actual - NOMBRE DIFERENTE al property
    precio_actual_subquery = PrecioHultDelivery.objects.filter(
        hult_delivery=OuterRef('pk'),
        is_active=True,
        fecha_inicio__lte=date.today()
    ).order_by('-fecha_inicio').values('precio')[:1]
    
    # Query base con anotaciones - usando prefijo para evitar conflicto
    qs = HultDelivery.objects.filter(
        is_delete=False
    ).annotate(
        _precio_actual=Coalesce(
            Subquery(precio_actual_subquery, output_field=DecimalField()),
            Value(Decimal('0.00'))
        )
    ).order_by('id')

    if all:
        # Buscar frase completa en campos concatenados
        qs_concat = qs.annotate(
            busqueda_completa=Concat(
                'nombre', 
                Value(' '), 
                output_field=CharField()
            )
        ).filter(busqueda_completa__icontains=all)
        
        qs = qs.filter(
            Q(pk__in=qs_concat.values('pk'))
        ).distinct()
    
    # Filtros específicos
    if agregado_id:
        qs = qs.filter(id=agregado_id)
    
    if nombre:
        qs = qs.filter(nombre__icontains=nombre)

    # Calcular totales
    total_data = qs.count()
    total_pages = (total_data + page_size - 1) // page_size

    # Aplicar paginación
    start = (page - 1) * page_size
    end = start + page_size
    page_items = list(qs[start:end])

    # Serializar los datos - usar el valor anotado
    items = []
    for item in page_items:
        items.append({
            "id": item.id,
            "nombre": item.nombre,
            "precio_actual": getattr(item, '_precio_actual', 0)  # Usar el campo anotado
        })

    return {
        "data": items,
        "totalData": total_data,
        "totalPages": total_pages,
        "currentPage": page
    }
    
    
@router.get("agregados/precios", tags=tag, response=ListResponse, auth=JWTAuth())
@permission_required('administracion.view_agregado')
def agregados_precios(
    request: HttpRequest,
    page: int = Query(1, description="Número de página"),
    page_size: int = Query(10, description="Cantidad de elementos por página"),
    all: str = Query(None, description="Búsqueda general en todos los campos"),
    agregado_id: int = Query(None, description="Filtrar por ID de agregado"),
    nombre: str = Query(None, description="Filtrar por nombre"),
    descripcion: str = Query(None, description="Filtrar por descripción")
):
    # Validar y ajustar parámetros de paginación
    page = max(1, page)
    page_size = min(max(1, page_size), 100)

    # Subquery para obtener el precio actual - NOMBRE DIFERENTE al property
    precio_actual_subquery = AgregadoPrecio.objects.filter(
        agregado=OuterRef('pk'),
        is_active=True,
        fecha_inicio__lte=date.today()
    ).order_by('-fecha_inicio').values('precio')[:1]
    
    # Query base con anotaciones - usando prefijo para evitar conflicto
    qs = Agregado.objects.filter(
        is_delete=False
    ).annotate(
        _precio_actual=Coalesce(
            Subquery(precio_actual_subquery, output_field=DecimalField()),
            Value(Decimal('0.00'))
        )
    ).order_by('id')

    if all:
        # Buscar frase completa en campos concatenados
        qs_concat = qs.annotate(
            busqueda_completa=Concat(
                'nombre', 
                Value(' '), 
                'descripcion',
                output_field=CharField()
            )
        ).filter(busqueda_completa__icontains=all)
        
        qs = qs.filter(
            Q(pk__in=qs_concat.values('pk'))
        ).distinct()
    
    # Filtros específicos
    if agregado_id:
        qs = qs.filter(id=agregado_id)
    
    if nombre:
        qs = qs.filter(nombre__icontains=nombre)
    
    if descripcion:
        qs = qs.filter(descripcion__icontains=descripcion)

    # Calcular totales
    total_data = qs.count()
    total_pages = (total_data + page_size - 1) // page_size

    # Aplicar paginación
    start = (page - 1) * page_size
    end = start + page_size
    page_items = list(qs[start:end])

    # Serializar los datos - usar el valor anotado
    items = []
    for item in page_items:
        items.append({
            "id": item.id,
            "nombre": item.nombre,
            "descripcion": item.descripcion,
            "precio_actual": getattr(item, '_precio_actual', 0)  # Usar el campo anotado
        })

    return {
        "data": items,
        "totalData": total_data,
        "totalPages": total_pages,
        "currentPage": page
    }
    