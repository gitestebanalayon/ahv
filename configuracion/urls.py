from django.contrib import admin
from django.conf.urls.i18n import i18n_patterns
from django.urls    import include, path

from django.conf.urls.static import static
from django.conf import settings


from apps.frontend.views        import inicio
from apps.frontend.views        import debug_view

from .api import api

urlpatterns =   [
                    path("i18n/", include("django.conf.urls.i18n")),
                    path('debug/',              debug_view,   name='debug_view'),
                    path('',                    inicio,             name = 'inicio' ),
                    path("admin/",              admin.site.urls                     ),
                    path("",                    api.urls                            ),
                    path("maintenance-mode/",   include("maintenance_mode.urls")    ),

                ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT) + i18n_patterns(path("admin/", admin.site.urls),
    )
