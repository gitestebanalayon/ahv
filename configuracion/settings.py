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
# ALLOWED_HOSTS       = config('ALLOWED_HOSTS', cast=Csv())

ALLOWED_HOSTS = [
    'ahv-jcsu.onrender.com',
    'www.ahv-jcsu.onrender.com', 
    '.onrender.com',
    'localhost',
    '127.0.0.1',
    '172.16.0.78',  # Tu IP local si la necesitas
]


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
    'apps.auxiliares',
    'apps.sistema',
    'apps.frontend',
    'apps.administracion',
    'apps.proveedores',
]

THIRD_APPS = [
    'channels',
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

ASGI_APPLICATION = 'configuracion.asgi.application'

# REDIS_URL = config('REDIS_URL', default='redis://localhost:6379')


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer"
    },
}

# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [REDIS_URL],
#             "capacity": 1500,  # default 100
#             "expiry": 10,  # default 60
#         },
#     },
# }

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": REDIS_URL,
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "CONNECTION_POOL_KWARGS": {
#                 "max_connections": 50,
#                 "retry_on_timeout": True,
#             },
#             "IGNORE_EXCEPTIONS": True,
#             "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
#         }
#     }
# }

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Configuración de sesiones en Redis (opcional pero recomendado)
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 1209600  # 2 semanas


# CELERY_BROKER_URL = REDIS_URL
# CELERY_RESULT_BACKEND = REDIS_URL
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "visibility_timeout": 3600,
    "max_retries": 3,
}

# CELERY_ACCEPT_CONTENT = ["application/json"]
# CELERY_TASK_SERIALIZER = "json"
# CELERY_RESULT_SERIALIZER = "json"
# CELERY_TIMEZONE = TIME_ZONE

# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             "hosts": [('127.0.0.1', 6379)],
#         },
#     },
# }

# CHANNEL_LAYERS = {
#     "default": {
#         "BACKEND": "channels.layers.InMemoryChannelLayer"
#     },
# }


CSRF_TRUSTED_ORIGINS = [
    'https://ahv-jcsu.onrender.com',
    'https://www.ahv-jcsu.onrender.com',
    'https://*.onrender.com',
    'wss://*.onrender.com',  # Para WebSockets
]

# CSRF_COOKIE_DOMAIN = '.onrender.com'
# SESSION_COOKIE_DOMAIN = '.onrender.com'
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True
# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True

RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Configuración de seguridad para Render
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_BROWSER_XSS_FILTER = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRECLOAD = True

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False  # Importante: SSL y TLS no pueden ser True al mismo tiempo
EMAIL_HOST_USER = 'serviciosesteban953@gmail.com'
EMAIL_HOST_PASSWORD = 'ukftpyufxtmjkvkw'
 
DEFAULT_FROM_EMAIL = 'serviciosesteban953@gmail.com'
SERVER_EMAIL = 'serviciosesteban953@gmail.com'


MIDDLEWARE      =   [
                        'django.middleware.security.SecurityMiddleware',
                        'whitenoise.middleware.WhiteNoiseMiddleware',
                        'django.contrib.sessions.middleware.SessionMiddleware',
                        'simple_history.middleware.HistoryRequestMiddleware',
                        # Incluida
                        "corsheaders.middleware.CorsMiddleware",
                        "django.middleware.locale.LocaleMiddleware",
                        'django.middleware.common.CommonMiddleware',
                        'django.middleware.csrf.CsrfViewMiddleware',
                        'django.contrib.auth.middleware.AuthenticationMiddleware',
                        'django.contrib.messages.middleware.MessageMiddleware',
                        'django.middleware.clickjacking.XFrameOptionsMiddleware',
                        'maintenance_mode.middleware.MaintenanceModeMiddleware',
                        'apps.cuenta.middleware.RequestMiddleware',
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


DJANGO_REST_PASSWORDRESET_TOKEN_CONFIG = {
    'CLASS': 'django_rest_passwordreset.tokens.RandomNumberTokenGenerator',
    'OPTIONS': {
        'min_number': 10000,
        'max_number': 99999
    }
}


WSGI_APPLICATION = "configuracion.wsgi.application"


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases

DATABASES = {
                'default' :     {
                                    'ENGINE':           'django.db.backends.postgresql',
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

LANGUAGES = (
    ("es", _("Spanish")),
    ("en", _("English")),
)

TIME_ZONE           = 'America/Caracas'
USE_I18N            = True
DEFAULT_AUTO_FIELD  = 'django.db.models.BigAutoField'


STATIC_URL          = 'static/'
STATICFILES_DIRS    = [os.path.join(BASE_DIR, 'staticfiles/'),]
#STATIC_ROOT         = os.path.join(BASE_DIR, 'staticfiles/')
STATIC_ROOT         = os.path.join(BASE_DIR, 'static', )
MEDIA_ROOT          = os.path.join(BASE_DIR, 'media/')
MEDIA_URL           = '/media/'

STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'


CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://ahv-jcsu.onrender.com",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
CORS_ALLOW_CREDENTIALS = True

if DEBUG:
    CORS_ALLOWED_ORIGINS.append("http://localhost:3000")
    CORS_ALLOWED_ORIGINS.append("http://127.0.0.1:3000")

AUTH_USER_MODEL         = 'cuenta.User'
AUTH_PASSWORD_RESET_URL = "http://127.0.0.1:8000/<YOUR_PASSWORD_RESET_FRONTEND_URL>/"

MAINTENANCE_MODE = False  # True para activar mantenimiento
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
MAINTENANCE_MODE_IGNORE_SUPERUSER = True   # Permite acceso a superusuarios

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
# REDIS_URL                       =   os.getenv("BROKER_URL", "redis://localhost:6379")
# 4. Celery también usar Redis Cloud





# CACHES = {
#     "default": {
#         "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
#         "LOCATION": "unique-snowflake",
#     }
# }

# CACHES = {
#     "default": {
#         "BACKEND": "django_redis.cache.RedisCache",
#         "LOCATION": REDIS_URL,
#         "OPTIONS": {
#             "CLIENT_CLASS": "django_redis.client.DefaultClient",
#             "CONNECTION_POOL_KWARGS": {
#                 "max_connections": 50,
#                 "retry_on_timeout": True,
#             },
#             "IGNORE_EXCEPTIONS": True,
#         }
#     }
# }


# # Optional: This is to ensure Django sessions are stored in Redis
# SESSION_ENGINE      = 'django.contrib.sessions.backends.cache'
# SESSION_CACHE_ALIAS = 'default'

# 3. Sesiones en Redis
# SESSION_ENGINE = "django.contrib.sessions.backends.cache"
# SESSION_CACHE_ALIAS = "default"
# SESSION_COOKIE_AGE = 1209600  # 2 semanas



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
    # "SHOW_LANGUAGES": True,
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
    "SHOW_BACK_BUTTON": True,
    "ENVIRONMENT": "configuracion.settings.environment_callback",
    "DASHBOARD_CALLBACK": "configuracion.settings.dashboard_callback",
    "LOGIN": {
        # "image": lambda request: static("login-bg.jpg"),
    },
    # "EXTENSIONS": {
    #     "modeltranslation": {
    #         "flags": {
    #             "en": "🇬🇧",
    #             "fr": "🇫🇷",
    #             "nl": "🇧🇪",
    #         },
    #     },
    # },
    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": True,
    },
     "SITE_DROPDOWN": [
        {
            "icon": "diamond",  # Icono de Material Symbols opcional
            "title": _("Mi sitio externo"),
            "link": "https://ejemplo.com",
            "attrs": {
                "target": "_blank",  # Abre el enlace en una nueva pestaña
            },
        },
        {
            "icon": "dashboard",
            "title": _("Panel de administración"),
            "link": reverse_lazy("admin:index"),
        },
        # Puedes añadir más enlaces aquí
    ],
     
     
     "COLORS": 
                {
                    # "base": 
                    # {
                    #     #"50": "oklch(98.5% .002 247.839)",
                    #     #"100": "oklch(96.7% .003 264.542)",
                    #     #"200": "oklch(92.8% .006 264.531)",
                    #     #"300": "oklch(87.2% .01 258.338)",
                    #     #"400": "oklch(70.7% .022 261.325)",
                    #     #"500": "oklch(55.1% .027 264.364)",
                    #     "600": "oklch(44.6% .03 256.802)",
                    #     #"700": "oklch(37.3% .034 259.733)",
                    #     #"800": "oklch(27.8% .033 256.848)",
                    #     #"900": "oklch(21% .034 264.665)",
                    #     #"950": "oklch(13% .028 261.692)",
                    # },
                    
                    "primary": {
                        "50": "#e8f0f9",
                        "100": "#c5daf0",
                        "200": "#9dc2e7",
                        "300": "#75aade",
                        "400": "#4d92d5",
                        "500": "#257acc",    # Azul medio
                        "600": "#1164ad",    # TU COLOR PRINCIPAL
                        "700": "#0e508a",
                        "800": "#0a3c68",
                        "900": "#072845",
                        "950": "#041423",
                    },
                    
                    "orange": {
                        "50": "#fef4e6",
                        "100": "#fde5cc",
                        "200": "#fbd099",
                        "300": "#f9bb66",
                        "400": "#f7a633",
                        "500": "#f59100",      # Naranja más brillante/claro
                        "600": "#f08227",      # TU COLOR NARANJA (#f08227)
                        "700": "#c0661f",
                        "800": "#904a17",
                        "900": "#602e0f",
                        "950": "#301207",
                    },
                    
                    "green": {
                        "50": "#e8f9f2",
                        "100": "#c5f0e0",
                        "200": "#9de7cc",
                        "300": "#75deb9",
                        "400": "#4dd5a5",
                        "500": "#25cc92",      # Verde más claro/brillante
                        "600": "#10b981",      # TU COLOR VERDE (#10b981)
                        "700": "#0d9467",
                        "800": "#0a6f4d",
                        "900": "#064a34",
                        "950": "#03251a",
                    },
                    
                    "gray": {
                        "50": "oklch(98.5% 0.002 247.8)",
                        "100": "oklch(96.7% 0.003 264.5)",
                        "200": "oklch(92.8% 0.006 264.5)",
                        "300": "oklch(87.2% 0.010 258.3)",
                        "400": "oklch(70.7% 0.022 261.3)",
                        "500": "oklch(55.1% 0.027 264.4)",
                        "600": "oklch(44.6% 0.030 256.8)",
                        "700": "oklch(37.3% 0.034 259.7)",
                        "800": "oklch(27.8% 0.033 256.8)",
                        "900": "oklch(21.0% 0.034 264.7)",
                        "950": "oklch(13.0% 0.028 261.7)",
                    },
                    
                    "accent": {
                        "50": "oklch(97.5% 0.025 250.5)",
                        "100": "oklch(94.5% 0.045 250.1)",
                        "200": "oklch(90.5% 0.068 249.8)",
                        "300": "oklch(85.5% 0.092 249.5)",
                        "400": "oklch(80.5% 0.115 249.2)",
                        "500": "oklch(75.5% 0.135 248.9)",  # #afc5e1 equivalente (más claro)
                        "600": "oklch(65.5% 0.140 248.7)",
                        "700": "oklch(55.5% 0.130 248.5)",
                        "800": "oklch(45.5% 0.115 248.3)",
                        "900": "oklch(35.5% 0.095 248.1)",
                        "950": "oklch(25.5% 0.075 247.9)",
                    },
                    
                    "font": 
                    {
                        "subtle-light":     "var(--color-base-500)",  # text-base-500
                        "subtle-dark":      "var(--color-base-400)",  # text-base-400
                        "default-light":    "var(--color-base-600)",  # text-base-600
                        "default-dark":     "var(--color-base-300)",  # text-base-300
                        "important-light":  "var(--color-base-900)",  # text-base-900
                        "important-dark":   "var(--color-base-100)",  # text-base-100
                    },
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