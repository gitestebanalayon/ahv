from typing import Optional, List
from datetime import date, time, datetime
from ninja import Schema
from decimal import Decimal

class SchemaListarEntrega(Schema):
    id: int
    pedido_id: int
    codigo_entrega: str
    yardas_asignadas: Decimal
    
    @classmethod
    def from_orm(cls, entrega):
        return cls(
            id=entrega.id,
            pedido_id=entrega.pedido_id,
            codigo_entrega=entrega.codigo_entrega,
            yardas_asignadas=entrega.yardas_asignadas,
        )

class SchemaListarPedido(Schema):
    id: int
    codigo_pedido: str
    cantidad_yardas: Decimal
    entregas: List[SchemaListarEntrega] = []  # Lista de entregas, no una sola
    
    @classmethod
    def from_orm(cls, pedido):
        # Obtener todas las entregas asociadas a este pedido
        entregas_data = []
        
        # Verificar si podemos acceder a las entregas relacionadas
        if hasattr(pedido, 'entrega_set'):
            # Con prefetch_related, las entregas ya están cargadas
            for entrega in pedido.entrega_set.all():
                entregas_data.append(SchemaListarEntrega.from_orm(entrega))

        return cls(
            id=pedido.id,
            codigo_pedido=pedido.codigo_pedido,
            cantidad_yardas=pedido.cantidad_yardas,
            entregas=entregas_data
        )
        

class EntregaActionResponse(Schema):
    success: bool
    message: str
    estado: Optional[str] = None
    fecha_hora_salida: Optional[datetime] = None
    fecha_hora_entrega: Optional[datetime] = None
    conductor_disponible: Optional[bool] = None
    vehiculo_disponible: Optional[bool] = None
    pedido_estado: Optional[str] = None

class EntregaActionRequest(Schema):
    motivo: Optional[str] = None  # Para cancelaciones