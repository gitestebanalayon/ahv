# configuracion/asgi.py
import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
import apps.sistema.websocket.routing  # Si tienes routing de WebSockets

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion.settings')
django.setup()

# Aplicación ASGI para HTTP y WebSockets
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                apps.sistema.websocket.routing.websocket_urlpatterns  # Tus rutas de WebSockets
            )
        )
    ),
})