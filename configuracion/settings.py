from pathlib import Path
from django.templatetags.static import static
from datetime       import timedelta
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from decouple       import config, Csv

import os
import logging.config

BASE_DIR            = Path(__file__).resolve().parent.parent
SECRET_KEY          = config('SECRET_KEY')
DEBUG               = config('DEBUG')
ALLOWED_HOSTS       = config('ALLOWED_HOSTS', cast=Csv())


# Application definition

BASE_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",  # optional, si se necesitan filtros especiales
    "unfold.contrib.forms",  # optional, si se necesitan elementos de formulario especiales
    "unfold.contrib.inlines",  # optional, si se necesitan líneas especiales
    "unfold.contrib.import_export",  # optional, si se utiliza el paquete django-import-export
    "unfold.contrib.guardian",  # optional, si se utiliza el paquete django-guardian
    "unfold.contrib.simple_history",  # optional, si se utiliza el paquete django-simple-history
    "unfold.contrib.location_field",  # optional, si se utiliza el paquete django-location-field
    "unfold.contrib.constance",  # optional, si se utiliza el paquete django-constance
    "django.contrib.admin",  # required
    
    # Django core apps (OBLIGATORIAS)
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages", 
    "django.contrib.staticfiles",
]

LOCAL_APPS = [
    'apps.cuenta',
    'apps.frontend',
]

THIRD_APPS = [
    'corsheaders',
    'ninja_extra',
    'ninja_jwt',
    'ninja_jwt.token_blacklist',
    'django_rest_passwordreset',
    #'guardian',
    'import_export',
    'maintenance_mode',
]

INSTALLED_APPS = BASE_APPS + LOCAL_APPS + THIRD_APPS

MIDDLEWARE      =   [
                        'django.middleware.security.SecurityMiddleware',
                        'django.contrib.sessions.middleware.SessionMiddleware',
                        # Incluida
                        "corsheaders.middleware.CorsMiddleware",
                        'django.middleware.common.CommonMiddleware',
                        'django.middleware.csrf.CsrfViewMiddleware',
                        'django.contrib.auth.middleware.AuthenticationMiddleware',
                        'django.contrib.messages.middleware.MessageMiddleware',
                        'django.middleware.clickjacking.XFrameOptionsMiddleware',
                        'maintenance_mode.middleware.MaintenanceModeMiddleware',
                    ]

ROOT_URLCONF = "configuracion.urls"

TEMPLATES       =   [
                        {
                            'BACKEND'   :   'django.template.backends.django.DjangoTemplates',
                            'DIRS'      :   [os.path.join(BASE_DIR, 'templates')],
                            'APP_DIRS'  :   True,
                            'OPTIONS'   :   {
                                                'context_processors': 
                                                [
                                                    'django.template.context_processors.debug',
                                                    'django.template.context_processors.request',
                                                    'django.contrib.auth.context_processors.auth',
                                                    'django.contrib.messages.context_processors.messages',
                                                ],
                                            },
                        },
                    ]

WSGI_APPLICATION = "configuracion.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
                'default' :     {
                                    'ENGINE':           'django.db.backends.mysql',
                                    'NAME':             config('DB_PRINCIPAL'),
                                    'USER':             config('USUARIO_PRODUCCION'),
                                    'PASSWORD':         config('CLAVE_PRODUCCION'),
                                    'HOST':             config('IP_PRODUCCION'),
                                    'PORT':             config('PUERTO_PREDETERMINADO'),
                                    # PARA LEER CON InspectDB un esquema especifico
                                    #'OPTIONS': {'options': '-c search_path=cuenta'}
                                },
            }


AUTH_USER_MODEL             =   'cuenta.User'
AUTH_PASSWORD_VALIDATORS    =   [
                                    { 'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',   },
                                    { 'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',             },
                                    { 'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',            },
                                    { 'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',           },
                                ]

AUTHENTICATION_BACKENDS     =   [
                                    'django.contrib.auth.backends.ModelBackend', # default
                                    #'guardian.backends.ObjectPermissionBackend',        
                                ]


LANGUAGE_CODE       = 'es-ve'
TIME_ZONE           = 'America/Caracas'
USE_I18N            = True
DEFAULT_AUTO_FIELD  = 'django.db.models.BigAutoField'

STATIC_URL          = 'static/'
STATICFILES_DIRS    = [os.path.join(BASE_DIR, 'staticfiles/'),]
#STATIC_ROOT         = os.path.join(BASE_DIR, 'staticfiles/')
STATIC_ROOT         = os.path.join(BASE_DIR, 'static', )
MEDIA_ROOT          = os.path.join(BASE_DIR, 'media/')
MEDIA_URL           = '/media/'


CORS_ALLOW_ALL_ORIGINS          =   True # Si esta en True acepta peticiones de cualquier origen 
                                         # Si esta en True entonces `CORS_ALLOWED_ORIGINS` no tendra efecto
CORS_ALLOW_CREDENTIALS          =   True

'''
CORS_ALLOWED_ORIGINS =  [
                            "https://example.com",
                        ]
'''
AUTH_USER_MODEL         = 'cuenta.User'
AUTH_PASSWORD_RESET_URL = "http://127.0.0.1:8000/<YOUR_PASSWORD_RESET_FRONTEND_URL>/"

MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True

# Logging Configuration

# Clear prev config
LOGGING_CONFIG = None

# Get log_level from env
LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "info").upper()

logging.config.dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters":   {
                            "console":  {
                                            "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %("
                                            "message)s",
                                        },
                        },
        "handlers":     {
                            "console": 
                                        {
                                            "class": "logging.StreamHandler",
                                            "formatter": "console",
                                        },
                        },
        "loggers":      {
                            "":         {
                                            "level": LOG_LEVEL,
                                            "handlers": ["console",],
                                        },
                        },
    }
)

# Configuracion del SWagger
SWAGGER_SETTINGS =  {
                        "USE_SESSION_AUTH": False,
                        "api_version":      "0.1",
                        "SECURITY_DEFINITIONS": {"api_key": {"type": "apiKey", "name": "Authorization", "in": "header"},},
                    }

# Configuracion de CELERY
REDIS_URL                       =   os.getenv("BROKER_URL", "redis://localhost:6379")
CELERY_BROKER_URL               =   REDIS_URL
CELERY_BROKER_TRANSPORT_OPTIONS =   {
                                        "visibility_timeout": 3600,  # 1 hour
                                    }
CELERY_ACCEPT_CONTENT           =   ["application/json"]
CELERY_TASK_SERIALIZER          =   "json"
CELERY_RESULT_SERIALIZER        =   "json"
CELERY_TIMEZONE                 =   TIME_ZONE


CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Optional: This is to ensure Django sessions are stored in Redis
SESSION_ENGINE      = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

#NINJA_JWT                       = {'TOKEN_OBTAIN_PAIR_INPUT_SCHEMA': 'apps.cuenta.views.token.MyTokenObtainPairInputSchema',}
# Configuracion del uso de JWT
NINJA_JWT                       =   {
                                        'ACCESS_TOKEN_LIFETIME':    timedelta(days=1),
                                        #'ACCESS_TOKEN_LIFETIME':    timedelta(minutes=5),
                                        'REFRESH_TOKEN_LIFETIME':   timedelta(days=1),
                                        'ROTATE_REFRESH_TOKENS':    False,
                                        'BLACKLIST_AFTER_ROTATION': True,
                                        'UPDATE_LAST_LOGIN':        True,

                                        'ALGORITHM':                'HS256',
                                        'SIGNING_KEY':              config('SECRET_KEY'),
                                        'VERIFYING_KEY':            None,
                                        'AUDIENCE':                 None,
                                        'ISSUER':                   None,
                                        'JWK_URL':                  None,
                                        'LEEWAY':                   0,

                                        'USER_ID_FIELD':            'id',
                                        'USER_ID_CLAIM':            'user_id',
                                        'USER_AUTHENTICATION_RULE': 'ninja_jwt.authentication.default_user_authentication_rule',

                                        'AUTH_TOKEN_CLASSES':       ('ninja_jwt.tokens.AccessToken',),
                                        'TOKEN_TYPE_CLAIM':         'token_type',
                                        'TOKEN_USER_CLASS':         'ninja_jwt.models.TokenUser',

                                        'JTI_CLAIM':                        'jti',

                                        'SLIDING_TOKEN_REFRESH_EXP_CLAIM':  'refresh_exp',
                                        'SLIDING_TOKEN_LIFETIME':           timedelta(minutes=5),
                                        'SLIDING_TOKEN_REFRESH_LIFETIME':   timedelta(days=1),

                                        # For Controller Schemas
                                        # FOR OBTAIN PAIR
                                        'TOKEN_OBTAIN_PAIR_INPUT_SCHEMA':           "ninja_jwt.schema.TokenObtainPairInputSchema",
                                        'TOKEN_OBTAIN_PAIR_REFRESH_INPUT_SCHEMA':   "ninja_jwt.schema.TokenRefreshInputSchema",
                                        # FOR SLIDING TOKEN
                                        'TOKEN_OBTAIN_SLIDING_INPUT_SCHEMA':        "ninja_jwt.schema.TokenObtainSlidingInputSchema",
                                        'TOKEN_OBTAIN_SLIDING_REFRESH_INPUT_SCHEMA':"ninja_jwt.schema.TokenRefreshSlidingInputSchema",

                                        'TOKEN_BLACKLIST_INPUT_SCHEMA':             "ninja_jwt.schema.TokenBlacklistInputSchema",
                                        'TOKEN_VERIFY_INPUT_SCHEMA':                "ninja_jwt.schema.TokenVerifyInputSchema",
                                    }

# Configuración UNFOLD
UNFOLD = {
    "SITE_TITLE": "AHV Admin",
    "SITE_HEADER": "Panel de Administración",
    "SITE_SUBHEADER": "Bienvenido al sistema",
    "SITE_SYMBOL": "speed",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "SHOW_BACK_BUTTON": True,
    "ENVIRONMENT": "configuracion.settings.environment_callback",
    "DASHBOARD_CALLBACK": "configuracion.settings.dashboard_callback",
    "THEME": "dark",
    "SHOW_THEME_TOGGLE": True,
    "LOGIN": {
        # "image": lambda request: static("login-bg.jpg"),
    },
    "COLOR_SCHEME": {
        # Colores específicos para modo claro
        "light": {
            "primary": {
                "50": "oklch(97.7% .014 308.299)",
                "100": "oklch(94.6% .033 307.174)",
                "200": "oklch(90.2% .063 306.703)",
                "300": "oklch(82.7% .119 306.383)",
                "400": "oklch(71.4% .203 305.504)",
                "500": "oklch(62.7% .265 303.9)",
                "600": "oklch(55.8% .288 302.321)",
                "700": "oklch(49.6% .265 301.924)",
                "800": "oklch(43.8% .218 303.724)",
                "900": "oklch(38.1% .176 304.987)",
                "950": "oklch(29.1% .149 302.717)",
            },
        },
        # Colores específicos para modo oscuro
        "dark": {
            "primary": {
                "50": "oklch(97.7% .014 308.299)",
                "100": "oklch(94.6% .033 307.174)",
                "200": "oklch(90.2% .063 306.703)",
                "300": "oklch(82.7% .119 306.383)",
                "400": "oklch(71.4% .203 305.504)",
                "500": "oklch(62.7% .265 303.9)",
                "600": "oklch(55.8% .288 302.321)",
                "700": "oklch(49.6% .265 301.924)",
                "800": "oklch(43.8% .218 303.724)",
                "900": "oklch(38.1% .176 304.987)",
                "950": "oklch(29.1% .149 302.717)",
            },
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": True,
        "navigation": [
            {
                "title": _("Navegación"),
                "separator": True,
                "items": [
                    {
                        "title": _("Dashboard"),
                        "icon": "dashboard",
                        "link": "/admin/",
                        "permission": lambda request: request.user.is_superuser,
                    },
                    {
                        "title": _("Usuarios"),
                        "icon": "account_circle",
                        "link": "/admin/cuenta/user",
                        "permission": lambda request: request.user.is_authenticated,
                    },
                    {
                        "title": _("Grupos"),
                        "icon": "people",
                        "link": "/admin/auth/group",
                        "permission": lambda request: request.user.is_authenticated,
                    },
                ],
            },
        ],
    },
}


# Callbacks para UNFOLD
def environment_callback(request):
    """
    Callback para mostrar el entorno en la esquina superior derecha
    """
    if DEBUG:
        return ["Desarrollo", "warning"]
    else:
        return ["Producción", "danger"]


def dashboard_callback(request, context):
    """
    Callback para el dashboard personalizado
    """
    # Puedes agregar datos personalizados aquí
    context.update({
        "custom_message": "Bienvenido al panel de administración",
    })
    return context