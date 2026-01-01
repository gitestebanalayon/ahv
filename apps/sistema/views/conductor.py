from ninja import Router, Query
from ninja_jwt.authentication import JWTAuth
from django.http import HttpRequest
from ninja.errors import HttpError
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat

from apps.sistema.models.conductor import Conductor
from apps.sistema.schemas.conductor import  SchemaListar
from apps.schemas.list_response import ListResponse
from apps.schemas.types_messages import SuccessSchema, ErrorSchema

from apps.decoradores.verificar_permisos import permission_required

tag = ['Conductores']
router = Router()


# @permission_required('sistema.view_conductor')
@router.get("/listar", tags=tag, response=ListResponse)
def listar(
    request: HttpRequest,
    page: int = Query(1, description="Número de página"),
    page_size: int = Query(10, description="Cantidad de elementos por página"),
    all: str = Query(None, description="Búsqueda general en todos los campos"),
    conductor_id: int = Query(None, description="Filtrar por ID de conductor"),
    matricula: str = Query(None, description="Filtrar por matrícula de vehículo"),
    alias_vehiculo: str = Query(None, description="Filtrar por alias del vehículo"),
):
    # Validar y ajustar parámetros de paginación
    page = max(1, page)
    page_size = min(max(1, page_size), 100)

    # Query base con select_related usando el nombre correcto 'vehiculo'
    qs = Conductor.objects.filter().select_related('vehiculo').order_by('id')

    if all:
        # Opción A: Buscar frase completa en campos concatenados
        qs_concat = qs.annotate(
            busqueda_completa=Concat(
                'nombre', 
                Value(' '), 
                'descripcion',
                output_field=CharField()
            )
        ).filter(busqueda_completa__icontains=all)
        
        # También buscar en datos del vehículo relacionado
        qs_vehiculos = qs.filter(
            Q(vehiculo__matricula__icontains=all) |
            Q(vehiculo__alias__icontains=all) |
            Q(vehiculo__modelo__icontains=all) |
            Q(vehiculo__marca__icontains=all)
        ).distinct()

        qs = qs.filter(
            Q(pk__in=qs_concat.values('pk')) |
            Q(pk__in=qs_vehiculos.values('pk'))
        ).distinct()
    
    # Filtros específicos
    if conductor_id:
        qs = qs.filter(id=conductor_id)
    
    # Filtros para vehículo
    if matricula:
        qs = qs.filter(vehiculo__matricula__icontains=matricula)
    
    if alias_vehiculo:
        qs = qs.filter(vehiculo__alias__icontains=alias_vehiculo)

    # Calcular totales
    total_data = qs.count()
    total_pages = (total_data + page_size - 1) // page_size

    # Aplicar paginación
    start = (page - 1) * page_size
    end = start + page_size
    page_items = list(qs[start:end])

    # Serializar los datos
    items = [SchemaListar.from_orm(item) for item in page_items]

    return {
        "data": items,
        "totalData": total_data,
        "totalPages": total_pages,
        "currentPage": page
    }