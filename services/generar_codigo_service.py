# services/calculos_pedido_service.py
from decimal import Decimal
from django.utils import timezone
from django.db.models import Q

class GenerarCodigoService:
    """
    Servicio que encapsula toda la lógica de cálculos de pedidos
    """
    
    def __init__(self, pedido):
        """
        Inicializa el servicio con un pedido
        """
        self.pedido = pedido
    
    