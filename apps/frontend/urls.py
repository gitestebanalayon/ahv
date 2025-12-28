from django.urls            import path
from apps.frontend.views    import documentacion, recuperar_clave

urlpatterns =   [
                    path('',                                               documentacion,              name = 'documentacion'                  ),
                    path('recuperar_clave/<str: uidb64>/<str: token>/',    recuperar_clave,   name = 'confirmar-reinicio-clave'       ),
                ]