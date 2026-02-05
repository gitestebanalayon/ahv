from ninja_extra                                import NinjaExtraAPI
from apps.cuenta.exceptions.auth                import BadRequestException
from datetime                                   import datetime
from ninja.responses                            import Response
from ninja.errors                               import ValidationError as NinjaValidationError
from pydantic                                   import ValidationError as PydanticValidationError

from django_rest_passwordreset.controller       import ResetPasswordController
from apps.cuenta.views.auth                     import CustomResetPasswordController
from apps.cuenta.views.auth                     import CrearCuentaController
from apps.cuenta.views.auth                     import AuthController
from apps.cuenta.views.usuario                  import UsuarioController

from apps.sistema.views.conductor import router as conductor
from apps.sistema.views.pedido import router as pedido

api = NinjaExtraAPI(
                        title           = "AHV",
                        description     = "API de AHV",
                        urls_namespace  = "demostrador",
                    )

# Manejador genérico para ValidationError (422)
def handle_validation_error_generic(request, exc):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Obtener los errores - FIJATE: exc.errors podría ser una función
    errors = getattr(exc, 'errors', None)
    
    # IMPORTANTE: Si errors es una función, llámala
    if callable(errors):
        try:
            errors = errors()
        except Exception:
            errors = None
    
    # Si errors es None, intenta obtener error_dict
    if not errors and hasattr(exc, 'error_dict'):
        errors = exc.error_dict
    
    # Si aún no hay errors, usa un mensaje genérico
    if not errors:
        return Response(
            {
                "statusCode": 422,
                "message": "Error de validación",
                "path": request.path, 
                "timestamp": timestamp
            },
            status=422
        )
    
    # Si errors es un diccionario (de Django), conviértelo a lista
    if isinstance(errors, dict):
        errors_list = []
        for field, field_errors in errors.items():
            if isinstance(field_errors, list):
                for error in field_errors:
                    errors_list.append({
                        'loc': [field],
                        'msg': str(error),
                        'type': 'validation_error'
                    })
        errors = errors_list
    
    # Ahora errors debería ser una lista
    if isinstance(errors, list) and len(errors) > 0:
        first_error = errors[0]
        
        # Verificar que first_error es un diccionario
        if not isinstance(first_error, dict):
            error_message = str(first_error)
            return Response(
                {
                    "statusCode": 422,
                    "message": error_message,
                    "path": request.path,
                    "timestamp": timestamp
                },
                status=422
            )
        
        # Extraer datos del error
        error_message = first_error.get('msg', 'Error de validación')
        error_loc = first_error.get('loc', [])
        
        # Extraer el nombre del campo del loc
        field_name = None
        for item in error_loc:
            if isinstance(item, str) and item not in ['body', 'query', 'path', 'header', 'cookie', 'data']:
                field_name = item
                break
        
        # Limpiar el mensaje
        if error_message.startswith('Value error, '):
            error_message = error_message[13:]
        
        # Mejorar mensajes específicos
        if error_message == 'Field required' and field_name:
            error_message = f"El campo '{field_name}' es requerido"
        elif field_name and error_message != 'Field required':
            error_message = f"{error_message}"
        
        return Response(
            {
                "statusCode": 422,
                "message": error_message,
                "path": request.path,
                "timestamp": timestamp
            },
            status=422
        )
    
    # Caso por defecto
    return Response(
        {
            "statusCode": 422,
            "message": "Error de validación",
            "path": request.path, 
            "timestamp": timestamp
        },
        status=422
    )

# Manejador para BadRequestException (400) con el mismo formato que 422
@api.exception_handler(BadRequestException)
def handle_bad_request_exception(request, exc):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return Response(
        {
            "statusCode": 400,
            "message": str(exc.detail),
            "url": request.path,
            "timestamp": timestamp
        },
        status=400
    )

# Registrar para ambos tipos de ValidationError
@api.exception_handler(NinjaValidationError)
def handle_ninja_validation_error(request, exc):
    return handle_validation_error_generic(request, exc)

@api.exception_handler(PydanticValidationError)
def handle_pydantic_validation_error(request, exc):
    return handle_validation_error_generic(request, exc)


api.register_controllers(
    ResetPasswordController,
    CustomResetPasswordController,
    CrearCuentaController,
    AuthController,
    UsuarioController
)

api.add_router("/conductor/",           conductor           )
api.add_router("/pedido/",              pedido              )