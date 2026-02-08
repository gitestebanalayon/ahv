import os
import sys

# ============================================
# WSGI PARA PYTHONANYWHERE CON PYTHON 3.13
# ============================================

print("🚀 INICIANDO APLICACIÓN DJANGO CHANNELS", file=sys.stderr)

# Configuración
BASE = '/home/ahv/ahv'
CONFIG = f'{BASE}/configuracion'
VENV_SITE = f'{BASE}/.venv/lib/python3.13/site-packages'

# Verificar Python 3.13
if not os.path.exists(VENV_SITE):
    print(f"❌ ERROR: No existe {VENV_SITE}", file=sys.stderr)
    raise RuntimeError("El entorno virtual debe ser Python 3.13")

# Configurar sys.path
sys.path = []
sys.path.insert(0, VENV_SITE)
sys.path.insert(0, CONFIG)
sys.path.insert(0, BASE)

# Configurar Redis Cloud
REDIS_URL = 'redis://default:QmYUKh6wDC6FkqmlBwnuRoyIB6P12sBq@redis-14617.c258.us-east-1-4.ec2.cloud.redislabs.com:14617'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'configuracion.settings')
os.environ['REDIS_URL'] = REDIS_URL
os.environ['PYTHONANYWHERE'] = 'true'
os.environ['WEBSOCKET_SUPPORT'] = 'true'

print(f"✅ Configuración completada", file=sys.stderr)

# Cargar aplicación ASGI
from configuracion.asgi import application
print(f"✅ Aplicación ASGI cargada", file=sys.stderr)