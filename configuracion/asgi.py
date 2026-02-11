import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion.settings')
django.setup()

# Importar después de configurar Django
from apps.sistema.websocket.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})

# configuracion/asgi.py
# import os
# from django.core.asgi import get_asgi_application
# from channels.routing import ProtocolTypeRouter, URLRouter
# from channels.auth import AuthMiddlewareStack
# # ❌ ELIMINA esta importación:
# # from channels.security.websocket import AllowedHostsOriginValidator
# import django

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion.settings')
# django.setup()

# from apps.sistema.websocket.routing import websocket_urlpatterns

# # ✅ VERSIÓN CORREGIDA - Sin AllowedHostsOriginValidator
# application = ProtocolTypeRouter({
#     "http": get_asgi_application(),
#     "websocket": AuthMiddlewareStack(  # Solo AuthMiddlewareStack
#         URLRouter(
#             websocket_urlpatterns
#         )
#     ),
# })