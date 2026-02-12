# apps/administracion/api/precios_unificados.py
from ninja import Router, Query
from ninja_jwt.authentication import JWTAuth
from django.http import HttpRequest
from django.db.models import Q, OuterRef, Subquery, DecimalField, F, Value
from django.db.models.functions import Coalesce
from decimal import Decimal
from datetime import date
from typing import List, Optional, Dict, Any

from apps.administracion.models.tipo_concreto import TipoConcreto
from apps.administracion.models.tipo_concreto_precio import TipoConcretoPrecio
from apps.administracion.models.hult_delivery import HultDelivery
from apps.administracion.models.precio_hult_delivery import PrecioHultDelivery
from apps.administracion.models.agregado import Agregado
from apps.administracion.models.agregado_precio import AgregadoPrecio

from apps.schemas.list_response import ListResponse
from apps.decoradores.verificar_permisos import permission_required

from ninja import Schema
from ninja.pagination import paginate
from pydantic import ConfigDict

tag = ['Precios Unificados']
router = Router()

# ============= SCHEMAS =============
class TipoConcretoPrecioSchema(Schema):
    id: int
    nombre: str
    descripcion: Optional[str] = ""
    precio_actual: float = 0.00

    model_config = ConfigDict(from_attributes=True)

class HultDeliveryPrecioSchema(Schema):
    id: int
    nombre: str
    yarda_minima: Optional[float]
    yarda_maxima: Optional[float]
    precio_actual: float = 0.00

    model_config = ConfigDict(from_attributes=True)

class AgregadoPrecioSchema(Schema):
    id: int
    nombre: str
    descripcion: Optional[str] = ""
    precio_actual: float = 0.00
    
    model_config = ConfigDict(from_attributes=True)

class PreciosUnificadosResponse(Schema):
    tipos_concreto: List[TipoConcretoPrecioSchema]
    hult_delivery: List[HultDeliveryPrecioSchema]
    agregados: List[AgregadoPrecioSchema]
    total_tipos_concreto: int
    total_hult_delivery: int
    total_agregados: int

# ============= API UNIFICADA =============
# @permission_required(['administracion.view_tipoconcreto', 'administracion.view_hultdelivery', 'administracion.view_agregado'], require_all=False)
@router.get("/precios/unificados", tags=tag, response=PreciosUnificadosResponse, auth=JWTAuth())
def precios_unificados(
    request: HttpRequest,
    incluir_tipos_concreto: bool = Query(True, description="Incluir tipos de concreto"),
    incluir_hult_delivery: bool = Query(True, description="Incluir Hult Delivery"),
    incluir_agregados: bool = Query(True, description="Incluir agregados"),
    search: str = Query(None, description="Búsqueda general en todos los items"),
    limit_por_categoria: int = Query(50, description="Límite de items por categoría")
):
    """
    API unificada que devuelve todos los precios actuales en una sola llamada.
    Reduce 3 peticiones a 1.
    """
    fecha_actual = date.today()
    resultado = {
        "tipos_concreto": [],
        "hult_delivery": [],
        "agregados": [],
        "total_tipos_concreto": 0,
        "total_hult_delivery": 0,
        "total_agregados": 0
    }
    
    # ===== 1. TIPOS DE CONCRETO =====
    if incluir_tipos_concreto:
        precio_subquery = TipoConcretoPrecio.objects.filter(
            tipo_concreto=OuterRef('pk'),
            is_active=True,
            fecha_inicio__lte=fecha_actual
        ).order_by('-fecha_inicio').values('precio')[:1]
        
        qs_concreto = TipoConcreto.objects.filter(
            is_delete=False
        ).annotate(
            precio_anotado=Coalesce(
                Subquery(precio_subquery),
                Value(0.00, output_field=DecimalField(max_digits=10, decimal_places=2))  # 👈 CORREGIDO
            )
        ).order_by('nombre')
        
        # Aplicar búsqueda si existe
        if search:
            qs_concreto = qs_concreto.filter(
                Q(nombre__icontains=search) | 
                Q(descripcion__icontains=search)
            )
        
        resultado["total_tipos_concreto"] = qs_concreto.count()
        
        # Serializar
        for item in qs_concreto[:limit_por_categoria]:
            resultado["tipos_concreto"].append({
                "id": item.id,
                "nombre": item.nombre,
                "descripcion": item.descripcion or "",
                "precio_actual": float(item.precio_anotado) if item.precio_anotado else 0.00
            })
    
    # ===== 2. HULT DELIVERY =====
    if incluir_hult_delivery:
        precio_subquery = PrecioHultDelivery.objects.filter(
            hult_delivery=OuterRef('pk'),
            is_active=True,
            fecha_inicio__lte=fecha_actual
        ).order_by('-fecha_inicio').values('precio')[:1]
        
        qs_hult = HultDelivery.objects.filter(
            is_delete=False
        ).annotate(
            precio_anotado=Coalesce(
                Subquery(precio_subquery),
                Value(0.00, output_field=DecimalField(max_digits=10, decimal_places=2))  # 👈 CORREGIDO
            )
        ).order_by('nombre')
        
        # Aplicar búsqueda si existe
        if search:
            qs_hult = qs_hult.filter(nombre__icontains=search)
        
        resultado["total_hult_delivery"] = qs_hult.count()
        
        # Serializar
        for item in qs_hult[:limit_por_categoria]:
            resultado["hult_delivery"].append({
                "id": item.id,
                "nombre": item.nombre,
                "yarda_minima": item.yarda_minima,
                "yarda_maxima": item.yarda_maxima,
                "precio_actual": float(item.precio_anotado) if item.precio_anotado else 0.00
            })
    
    # ===== 3. AGREGADOS =====
    if incluir_agregados:
        precio_subquery = AgregadoPrecio.objects.filter(
            agregado=OuterRef('pk'),
            is_active=True,
            fecha_inicio__lte=fecha_actual
        ).order_by('-fecha_inicio').values('precio')[:1]
        
        qs_agregados = Agregado.objects.filter(
            is_delete=False
        ).annotate(
            precio_anotado=Coalesce(
                Subquery(precio_subquery),
                Value(0.00, output_field=DecimalField(max_digits=10, decimal_places=2))  # 👈 CORREGIDO
            )
        ).order_by('nombre')
        
        # Aplicar búsqueda si existe
        if search:
            qs_agregados = qs_agregados.filter(
                Q(nombre__icontains=search) | 
                Q(descripcion__icontains=search)
            )
        
        resultado["total_agregados"] = qs_agregados.count()
        
        # Serializar
        for item in qs_agregados[:limit_por_categoria]:
            resultado["agregados"].append({
                "id": item.id,
                "nombre": item.nombre,
                "descripcion": item.descripcion or "",
                "precio_actual": float(item.precio_anotado) if item.precio_anotado else 0.00
            })
    
    return resultado