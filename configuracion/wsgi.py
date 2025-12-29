"""
WSGI config for configuracion project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""
# WSGI para esta estructura
# /var/www/ahvadmin_pythonanywhere_com_wsgi.py - VERSIÓN CORREGIDA
import os
import sys

# RUTA AL ENTORNO VIRTUAL
venv_path = '/home/ahvadmin/ahv/.venv'

# 1. Configurar el ejecutable de Python al del entorno virtual
python_executable = os.path.join(venv_path, 'bin', 'python3.12')
if os.path.exists(python_executable):
    sys.executable = python_executable

# 2. Agregar el site-packages del entorno virtual al path
site_packages = os.path.join(venv_path, 'lib', 'python3.12', 'site-packages')
if os.path.exists(site_packages) and site_packages not in sys.path:
    sys.path.insert(0, site_packages)

# 3. Agregar también la carpeta del proyecto
project_home = '/home/ahvadmin/ahv'
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# 4. Agregar la carpeta configuracion
configuracion_path = '/home/ahvadmin/ahv/configuracion'
if configuracion_path not in sys.path:
    sys.path.insert(0, configuracion_path)

# 5. Configurar la variable de entorno de Django
os.environ['DJANGO_SETTINGS_MODULE'] = 'configuracion.settings'

# 6. (Opcional) Verificar que podemos importar decouple antes de cargar Django
try:
    import decouple
    print(f"[WSGI] ✅ decouple importado desde: {decouple.__file__}", file=sys.stderr)
except ImportError as e:
    print(f"[WSGI] ❌ Error importando decouple: {e}", file=sys.stderr)
    # Mostrar sys.path para debugging
    print("[WSGI] sys.path:", file=sys.stderr)
    for p in sys.path:
        print(f"  {p}", file=sys.stderr)

# 7. Cargar la aplicación Django
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()