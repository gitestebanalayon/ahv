from ninja_extra.exceptions import APIException
from ninja_extra import status

# Crear excepciones personalizadas con códigos HTTP apropiados (solo para casos especiales de autenticación)

class UnauthorizedException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Credenciales inválidas"

class UserNotFoundInSystemException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Usuario no encontrado en sistema"

class InvalidPasswordException(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Contraseña incorrecta"
    
class BadRequestException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Solicitud incorrecta"