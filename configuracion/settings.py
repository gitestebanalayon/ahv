from pathlib import Path
from django.templatetags.static import static
from datetime import timedelta
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from decouple import config, Csv

import os
import logging.config

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', cast=Csv())

# ============================================
# DETECCIÓN AUTOMÁTICA DE ENTORNO
# ============================================

# Detectar PythonAnywhere
IN_PYTHONANYWHERE = 'PYTHONANYWHERE_DOMAIN' in os.environ or 'PYTHONANYWHERE' in os.environ
IS_DEVELOPMENT = DEBUG

print(f"🔍 Entorno detectado:")
print(f"   DEBUG: {DEBUG}")
print(f"   PythonAnywhere: {IN_PYTHONANYWHERE}")

# Application definition

BASE_APPS = [
    "unfold",  # before django.contrib.admin
    "unfold.contrib.filters",
    "unfold.contrib.forms",
    "unfold.contrib.inlines",
    "unfold.contrib.import_export",
    "unfold.contrib.guardian",
    "unfold.contrib.simple_history",
    "unfold.contrib.location_field",
    "unfold.contrib.constance",
    "django.contrib.admin",  # required
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
]

THIRD_APPS = [
    'channels',
    'corsheaders',
    'ninja_extra',
    'ninja_jwt',
    'ninja_jwt.token_blacklist',
    'django_rest_passwordreset',
    'import_export',
    'maintenance_mode',
]

INSTALLED_APPS = BASE_APPS + LOCAL_APPS + THIRD_APPS

# ============================================
# CONFIGURACIÓN ASGI/WEBSOCKETS
# ============================================

ASGI_APPLICATION = 'configuracion.asgi.application'

# ============================================
# CONFIGURACIÓN REDIS CLOUD PARA PYTHONANYWHERE
# ============================================

# Tu URL de Redis Cloud
REDIS_CLOUD_URL = 'redis://default:QmYUKh6wDC6FkqmlBwnuRoyIB6P12sBq@redis-14617.c258.us-east-1-4.ec2.cloud.redislabs.com:14617'

if IN_PYTHONANYWHERE:
    print("🚀 PythonAnywhere DETECTADO - Python 3.13")
    print("🔗 Usando REDIS CLOUD para WebSockets")
    
    # 1. CHANNELS CON REDIS CLOUD (OBLIGATORIO PARA WEBSOCKETS)
    CHANNEL_LAYERS = {
        'default': {
            'BACKEND': 'channels_redis.core.RedisChannelLayer',
            'CONFIG': {
                "hosts": [REDIS_CLOUD_URL],
                "capacity": 1500,
                "expiry": 10,
            },
        },
    }
    
    # 2. CACHE EN REDIS CLOUD
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_CLOUD_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "COMPRESSOR": "django_redis.compressors.zlib.ZlibCompressor",
                "IGNORE_EXCEPTIONS": True,
                "CONNECTION_POOL_KWARGS": {
                    "max_connections": 50,
                    "retry_on_timeout": True,
                }
            }
        }
    }
    
    # 3. SESIONES EN REDIS
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"
    SESSION_COOKIE_AGE = 1209600  # 2 semanas
    
    # 4. CELERY EN REDIS
    CELERY_BROKER_URL = REDIS_CLOUD_URL
    CELERY_RESULT_BACKEND = REDIS_CLOUD_URL
    CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
    CELERY_TASK_ALWAYS_EAGER = False
    
    # 5. CONFIGURACIÓN WEBSOCKET ESPECÍFICA
    # Asegurar que ALLOWED_HOSTS incluya tu dominio
    ALLOWED_HOSTS = [
        'ahv.pythonanywhere.com',
        'www.ahv.pythonanywhere.com',
        'localhost',
        '127.0.0.1',
    ]
    
    # Configuración CORS para WebSockets
    CORS_ALLOW_ALL_ORIGINS = True
    CORS_ALLOW_CREDENTIALS = True
    
    # Configuración CSRF para WebSockets
    CSRF_TRUSTED_ORIGINS = [
        'https://ahv.pythonanywhere.com',
        'wss://ahv.pythonanywhere.com',
    ]
    
else:
    # DESARROLLO LOCAL
    print("🔧 Desarrollo local detectado")
    REDIS_URL = config('REDIS_URL', default='redis://localhost:6379')
    
    # Usar Redis local o memoria
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        },
    }
    
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                "IGNORE_EXCEPTIONS": True,
            }
        }
    }
    
    SESSION_ENGINE = "django.contrib.sessions.backends.cache"
    SESSION_CACHE_ALIAS = "default"

# ============================================
# CONFIGURACIÓN EMAIL
# ============================================

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 465
EMAIL_USE_SSL = True
EMAIL_USE_TLS = False
EMAIL_HOST_USER = 'serviciosesteban953@gmail.com'
EMAIL_HOST_PASSWORD = 'ukftpyufxtmjkvkw'
DEFAULT_FROM_EMAIL = 'serviciosesteban953@gmail.com'
SERVER_EMAIL = 'serviciosesteban953@gmail.com'

# ============================================
# MIDDLEWARE
# ============================================

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
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

# ============================================
# URLS Y TEMPLATES
# ============================================

ROOT_URLCONF = "configuracion.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# ============================================
# CONFIGURACIÓN PASSWORD RESET
# ============================================

DJANGO_REST_PASSWORDRESET_TOKEN_CONFIG = {
    'CLASS': 'django_rest_passwordreset.tokens.RandomNumberTokenGenerator',
    'OPTIONS': {
        'min_number': 10000,
        'max_number': 99999
    }
}

WSGI_APPLICATION = "configuracion.wsgi.application"

# ============================================
# DATABASE
# ============================================

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_PRINCIPAL'),
        'USER': config('USUARIO_PRODUCCION'),
        'PASSWORD': config('CLAVE_PRODUCCION'),
        'HOST': config('IP_PRODUCCION'),
        'PORT': config('PUERTO_PREDETERMINADO'),
    },
}

# ============================================
# AUTENTICACIÓN
# ============================================

AUTH_USER_MODEL = 'cuenta.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
]

# ============================================
# INTERNACIONALIZACIÓN
# ============================================

LANGUAGE_CODE = 'es-ve'

LANGUAGES = (
    ("es", _("Spanish")),
    ("en", _("English")),
)

TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# ============================================
# ARCHIVOS ESTÁTICOS Y MEDIA
# ============================================

STATIC_URL = 'static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'staticfiles/'),]
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')
MEDIA_URL = '/media/'

# ============================================
# CONFIGURACIÓN CORS
# ============================================

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

AUTH_PASSWORD_RESET_URL = "http://127.0.0.1:8000/<YOUR_PASSWORD_RESET_FRONTEND_URL>/"

# ============================================
# MODO MANTENIMIENTO
# ============================================

MAINTENANCE_MODE = False
MAINTENANCE_MODE_IGNORE_ADMIN_SITE = True
MAINTENANCE_MODE_IGNORE_SUPERUSER = True

# ============================================
# LOGGING
# ============================================

LOGGING_CONFIG = None
LOG_LEVEL = os.getenv("DJANGO_LOG_LEVEL", "info").upper()

logging.config.dictConfig({
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "console": {
            "format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)s] %(module)s %(process)d %(thread)d %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "console",
        },
    },
    "loggers": {
        "": {
            "level": LOG_LEVEL,
            "handlers": ["console",],
        },
    },
})

# ============================================
# SWAGGER
# ============================================

SWAGGER_SETTINGS = {
    "USE_SESSION_AUTH": False,
    "api_version": "0.1",
    "SECURITY_DEFINITIONS": {"api_key": {"type": "apiKey", "name": "Authorization", "in": "header"},},
}

# ============================================
# CELERY
# ============================================

if IS_DEVELOPMENT and not IN_PYTHONANYWHERE:
    CELERY_BROKER_URL = REDIS_CLOUD_URL if IN_PYTHONANYWHERE else config('REDIS_URL', default='redis://localhost:6379')
    CELERY_RESULT_BACKEND = REDIS_CLOUD_URL if IN_PYTHONANYWHERE else config('REDIS_URL', default='redis://localhost:6379')
else:
    CELERY_BROKER_URL = REDIS_CLOUD_URL
    CELERY_RESULT_BACKEND = REDIS_CLOUD_URL

CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "visibility_timeout": 3600,
}
CELERY_ACCEPT_CONTENT = ["application/json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE

# ============================================
# NINJA JWT
# ============================================

NINJA_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(days=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': False,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': config('SECRET_KEY'),
    'VERIFYING_KEY': None,
    'AUDIENCE': None,
    'ISSUER': None,
    'JWK_URL': None,
    'LEEWAY': 0,
    'USER_ID_FIELD': 'id',
    'USER_ID_CLAIM': 'user_id',
    'USER_AUTHENTICATION_RULE': 'ninja_jwt.authentication.default_user_authentication_rule',
    'AUTH_TOKEN_CLASSES': ('ninja_jwt.tokens.AccessToken',),
    'TOKEN_TYPE_CLAIM': 'token_type',
    'TOKEN_USER_CLASS': 'ninja_jwt.models.TokenUser',
    'JTI_CLAIM': 'jti',
    'SLIDING_TOKEN_REFRESH_EXP_CLAIM': 'refresh_exp',
    'SLIDING_TOKEN_LIFETIME': timedelta(minutes=5),
    'SLIDING_TOKEN_REFRESH_LIFETIME': timedelta(days=1),
    'TOKEN_OBTAIN_PAIR_INPUT_SCHEMA': "ninja_jwt.schema.TokenObtainPairInputSchema",
    'TOKEN_OBTAIN_PAIR_REFRESH_INPUT_SCHEMA': "ninja_jwt.schema.TokenRefreshInputSchema",
    'TOKEN_OBTAIN_SLIDING_INPUT_SCHEMA': "ninja_jwt.schema.TokenObtainSlidingInputSchema",
    'TOKEN_OBTAIN_SLIDING_REFRESH_INPUT_SCHEMA': "ninja_jwt.schema.TokenRefreshSlidingInputSchema",
    'TOKEN_BLACKLIST_INPUT_SCHEMA': "ninja_jwt.schema.TokenBlacklistInputSchema",
    'TOKEN_VERIFY_INPUT_SCHEMA': "ninja_jwt.schema.TokenVerifyInputSchema",
}

# ============================================
# UNFOLD ADMIN
# ============================================

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
    "LOGIN": {},
    "SIDEBAR": {
        "show_search": False,
        "show_all_applications": True,
    },
    "SITE_DROPDOWN": [
        {
            "icon": "diamond",
            "title": _("Mi sitio externo"),
            "link": "https://ejemplo.com",
            "attrs": {"target": "_blank"},
        },
        {
            "icon": "dashboard",
            "title": _("Panel de administración"),
            "link": reverse_lazy("admin:index"),
        },
    ],
    "COLORS": {
        "primary": {
            "50": "#e8f0f9",
            "100": "#c5daf0",
            "200": "#9dc2e7",
            "300": "#75aade",
            "400": "#4d92d5",
            "500": "#257acc",
            "600": "#1164ad",
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
            "500": "#f59100",
            "600": "#f08227",
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
            "500": "#25cc92",
            "600": "#10b981",
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
            "500": "oklch(75.5% 0.135 248.9)",
            "600": "oklch(65.5% 0.140 248.7)",
            "700": "oklch(55.5% 0.130 248.5)",
            "800": "oklch(45.5% 0.115 248.3)",
            "900": "oklch(35.5% 0.095 248.1)",
            "950": "oklch(25.5% 0.075 247.9)",
        },
        "font": {
            "subtle-light": "var(--color-base-500)",
            "subtle-dark": "var(--color-base-400)",
            "default-light": "var(--color-base-600)",
            "default-dark": "var(--color-base-300)",
            "important-light": "var(--color-base-900)",
            "important-dark": "var(--color-base-100)",
        },
    },
}

# ============================================
# CALLBACKS UNFOLD
# ============================================

def environment_callback(request):
    if DEBUG:
        return ["Desarrollo", "warning"]
    else:
        return ["Producción", "danger"]

def dashboard_callback(request, context):
    context.update({
        "custom_message": "Bienvenido al panel de administración",
    })
    return context

# ============================================
# CONFIGURACIÓN ASGI.PY (EMBEBIDA)
# ============================================

# Nota: Esta configuración también está en configuracion/asgi.py
# pero la incluimos aquí para referencia
"""
import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion.settings')
django.setup()

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
"""