# apps/decoradores/verificar_permisos.py
from functools import wraps
from ninja.errors import HttpError
from decouple import config
import jwt
from apps.cuenta.models import User

def _get_user_from_token(request):
    """Función auxiliar para obtener usuario del token"""
    auth_header = request.headers.get('Authorization', '')
    
    if not auth_header.startswith('Bearer '):
        raise HttpError(401, "Token de autorización requerido")
    
    token = auth_header[7:]
    secret_key = config('SECRET_KEY')
    
    try:
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HttpError(401, "Token expirado")
    except jwt.InvalidTokenError:
        raise HttpError(401, "Token inválido")
    
    user_id = decoded.get('user_id')
    if not user_id:
        raise HttpError(401, "Token inválido: user_id no encontrado")
    
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        raise HttpError(401, "Usuario no encontrado")

def permission_required(permission_codename):
    """
    Decorador para endpoints Ninja normales (Router)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            user = _get_user_from_token(request)
            
            if not user.has_perm(permission_codename):
                raise HttpError(403, f"Permisos insuficientes")
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator

def permission_required_extra(permission_codename):
    """
    Decorador para endpoints Ninja Extra (api_controller)
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(self, *args, **kwargs):
            user = _get_user_from_token(self.context.request)
            
            if not user.has_perm(permission_codename):
                raise HttpError(403, f"Permisos insuficientes")
            
            return view_func(self, *args, **kwargs)
        return wrapped_view
    return decorator