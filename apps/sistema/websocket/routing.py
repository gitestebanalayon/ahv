from django.urls import path
from .consumers import PedidoConsumer

websocket_urlpatterns = [
    path('ws/pedidos/', PedidoConsumer.as_asgi()),
]


# from django.urls import path
# from .consumers import PedidoConsumer # Importamos la clase desde consumers.py

# websocket_urlpatterns = [
#     path('ws/pedidos/<str:operativo_nombre>/', PedidoConsumer.as_asgi())  # ✅ Con parámetro
# ]