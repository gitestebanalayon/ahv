from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth

from decouple import config
import jwt

from configuracion.schemes import SucessSchema, ErrorSchema
from apps.cuenta.models import User as Model
from apps.decoradores.verificar_permisos import permission_required_extra

from apps.cuenta.exceptions.auth import (
    BadRequestException
)
from apps.cuenta.schemes.usuario import (
    CreateUserSchema,
    UpdatePasswordSchema,
    UpdateEmailSchema,
    UpdateQASchema,
)

# CONTROLADOR PARA LA GESTION DE USUARIOS
@api_controller("/usuario", tags=['Usuarios'], auth=JWTAuth())
class UsuarioController():
    """Controller for all authentication operations"""
    
    @route.post(
        "/crear", 
        response={201: SucessSchema, 400: ErrorSchema, 422: ErrorSchema, 403: ErrorSchema}, 
        url_name="crear-usuario", 
        auth=JWTAuth()
    )
    @permission_required_extra('cuenta.add_user')
    def crear_usuario(self, user_schema: CreateUserSchema):
        """Create a new user account - Solo usuarios con permiso add_user"""
        try:
            # Extraer token y decodificar
            auth_header = self.context.request.headers.get('Authorization', '')
            
            if not auth_header.startswith('Bearer '):
                return 400, {"message": "Token de autorización requerido"}
            
            token = auth_header[7:]
            secret_key = config('SECRET_KEY')
            decoded = jwt.decode(token, secret_key, algorithms=["HS256"])
            
            # Crear usuario
            user = user_schema.create()
            return 201, {"message": "Usuario creado exitosamente"}
        
        except BadRequestException as e:
            return 400, {"message": str(e.detail)}
        
        except Exception as e:
            return 400, {"message": f"Error al crear usuario: {str(e)}"}

    @route.put(
        '/actualizar-password', 
        response={200: SucessSchema, 400: ErrorSchema, 404: ErrorSchema}
    )
    def actualizar_password(self, payload: UpdatePasswordSchema):
        """Change user password"""
        # NO captures APIException aquí - serán manejadas por el manejador global
        
        auth_header = self.context.request.headers.get('Authorization', '')
        
        if not auth_header.startswith('Bearer '):
            return 400, {"message": "Token de autorización requerido"}
        
        token = auth_header[7:]
        secret_key = config('SECRET_KEY')
        decoded = jwt.decode(token, secret_key, algorithms=["HS256"])

        user_id = int(decoded['user_id'])
        model = Model.objects.get(id=user_id)
        
        old_password = payload.old_password
        new_password = payload.new_password
        
        if model.check_password(old_password):
            model.set_password(new_password)
            model.save()
            return 200, {"message": "Contraseña cambiada exitosamente"}
        else:
            return 400, {"message": "Contraseña actual incorrecta"}

    @route.put(
        '/actualizar-email', 
        response={200: SucessSchema, 400: ErrorSchema, 404: ErrorSchema}
    )
    def actualizar_email(self, payload: UpdateEmailSchema):
        """Change user email address"""
        try:
            
            auth_header = self.context.request.headers.get('Authorization', '')
            
            if not auth_header.startswith('Bearer '):
                return 400, {"message": "Token de autorización requerido"}
            
            token = auth_header[7:]
            secret_key = config('SECRET_KEY')
            decoded = jwt.decode(token, secret_key, algorithms=["HS256"])

            user_id = int(decoded['user_id'])
           
            model = Model.objects.get(id=user_id)
            
            # Las validaciones se manejan automáticamente por el schema
            for attr, value in payload.dict().items():
                setattr(model, attr, value)
            model.save()
            
            return 200, {"message": "Correo electrónico actualizado exitosamente"}
        
        except BadRequestException as e:
            # Dejar que el manejador global se encargue del formato (400)
            raise e
            
        except Model.DoesNotExist:
            return 404, {"message": "Usuario no encontrado"}
        
        except Exception as e:
            return 400, {"message": f"Error al actualizar el correo: {str(e)}"}

    @route.put(
        '/actualizar-preguntas-respuestas', 
        response={200: SucessSchema, 404: ErrorSchema}
    )
    def actualizar_preguntas_y_respuestas(self, payload: UpdateQASchema):
        """Change user security question and answer"""
        try:
            auth_header = self.context.request.headers.get('Authorization', '')
            
            if not auth_header.startswith('Bearer '):
                return 400, {"message": "Token de autorización requerido"}
            
            token = auth_header[7:]
            secret_key = config('SECRET_KEY')
            decoded = jwt.decode(token, secret_key, algorithms=["HS256"])

            user_id = int(decoded['user_id'])
            
            
            model = Model.objects.get(id=user_id)
            
            # Las validaciones se manejan automáticamente por el schema
            for attr, value in payload.dict().items():
                setattr(model, attr, value)
            model.save()
            
            return 200, {"message": "Preguntas y respuestas de seguridad actualizadas exitosamente"}
        
        except Model.DoesNotExist:
            return 404, {"message": "Usuario no encontrado"}
        
        except Exception as e:
            return 400, {"message": f"Error al actualizar preguntas y respuestas: {str(e)}"}
