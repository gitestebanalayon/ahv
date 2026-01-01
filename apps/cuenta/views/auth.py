from ninja_jwt.controller import TokenObtainPairController
from ninja_extra import api_controller, route
from ninja_jwt.authentication import JWTAuth
from ninja_jwt import schema
from typing import List
from django_rest_passwordreset.models import ResetPasswordToken
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db import transaction
from django.contrib.auth.models import Group
from enum import Enum

from configuracion.schemes import SucessSchema, ErrorSchema

from ninja_extra.exceptions import APIException
from apps.cuenta.exceptions.auth import (
    UnauthorizedException,
    UserNotFoundInSystemException,
    InvalidPasswordException,
    BadRequestException,
)
from apps.cuenta.schemes.auth import (
    MyTokenObtainPairOutSchema,
    MyTokenObtainPairInputSchema,
    MyTokenObtainPairSchema
)

from apps.cuenta.schemes.usuario import (
    CreateUserSchema,
)




# CONTROLADOR PARA RESTABLECER LA CONTRASEÑA
@api_controller('/password_reset', tags=['Password Reset'], auth=None)
class CustomResetPasswordController:
    """
    Controlador personalizado para password reset
    """
    @route.post(
    "/",
    response={200: SucessSchema, 400: ErrorSchema},
    auth=None
    )
    def custom_password_reset(self, email: str):
        """Password reset personalizado que usa templates de rest_password_reset"""
        try:
            User = get_user_model()
            
            # Buscar usuarios con ese email
            users = User.objects.filter(email=email)
            
            if users.count() == 0:
                return 400, {"message": "Esta cuenta no existe"}
            
            # print(f"🔑 Creando tokens para {users.count()} usuarios...")
            
            tokens_created = []
            
            for user in users:
                # Eliminar tokens existentes para este usuario
                ResetPasswordToken.objects.filter(user=user).delete()
                
                # Crear nuevo token
                token = ResetPasswordToken.objects.create(
                    user=user,
                    user_agent="Custom Reset",
                    ip_address="127.0.0.1"
                )
                
                tokens_created.append({
                    'user': user,
                    'token': token
                })
                
                # print(f"   ✅ Token para {user.username}: {token.key}")
            
            # Enviar email usando los templates de rest_password_reset
            if users.count() == 1:
                # Si es un solo usuario, usar template normal
                # Contexto para el template
                context = {
                    'current_user': tokens_created[0]['user'],
                    'username': user.username,
                    'email': user.email,
                    'reset_password_token': tokens_created[0]['token'],
                }
                
                # Renderizar templates de rest_password_reset
                email_html_message = render_to_string('rest_password_reset/email.html', context)
                email_plaintext_message = render_to_string('rest_password_reset/email.txt', context)
                
                # Enviar email
                send_mail(
                    subject=f'🔐 Restablecer Contraseña',
                    message=email_plaintext_message,
                    from_email='serviciosesteban953@gmail.com',
                    recipient_list=[email],
                    html_message=email_html_message,
                    fail_silently=False,
                )

            # print(f"✅ Email enviado a {email} con {len(tokens_created)} tokens")
            
            return 200, {
                "message": f"Tokens creados para {len(tokens_created)} usuarios", 
                "users_found": len(tokens_created)
            }
            
        except Exception as e:
            # print(f"❌ Error en custom password reset: {e}")
            return 400, {"message": f"Error: {str(e)}"}

@api_controller('/crear-cuenta', tags=['Auth'], auth=None)
class CrearCuentaController:
    """Controller for creating new user accounts"""
    
    @route.post(
        "",
        response={201: SucessSchema, 400: ErrorSchema, 422: ErrorSchema, 403: ErrorSchema},
        url_name="crear-cuenta"
    )
    def crear_cuenta(
            self, user_schema: CreateUserSchema
        ):
        """Create a new user account and add to Clientes group"""
        try:           
            # Crear usuario y asignar al grupo Clientes en una transacción
            with transaction.atomic():
                # Crear usuario
                
                user = user_schema.create()
                
                # Obtener o crear el grupo "Clientes" usando get_or_create
                grupo_clientes, created = Group.objects.get_or_create(name='Clientes')
                # Agregar usuario al grupo
                user.groups.add(grupo_clientes)
                
            
            return 201, {"message": "Cuenta creada exitosamente."}
        
        except BadRequestException as e:
            return 400, {"message": str(e.detail)}
        
        except Exception as e:
            return 400, {"message": f"Error al crear usuario: {str(e)}"}

# CONTROLADOR PARA LA AUTENTICACIÓN
@api_controller("", tags=['Auth'], auth=JWTAuth())
class AuthController():
    """Controller for all authentication operations"""
    
    @route.post(
        "/login", 
        response={200: MyTokenObtainPairOutSchema, 401: ErrorSchema, 400: ErrorSchema, 500: ErrorSchema}, 
        url_name="token_obtain_pair",
        auth=None
    )
    def login(self, user_token: MyTokenObtainPairInputSchema):
        """Obtain JWT token pair"""
        try:
            token_schema = MyTokenObtainPairSchema(user_token)
            return token_schema.output_schema()
        except (UserNotFoundInSystemException, InvalidPasswordException, UnauthorizedException) as e:
            print(f"Excepción específica capturada: {type(e).__name__}: {e.detail}")
            return 401, {"message": str(e.detail)}
        except APIException as e:
            print(f"APIException genérica: {type(e).__name__}: {e.detail}, status: {e.status_code}")
            return e.status_code, {"message": str(e.detail)}
        except Exception as e:
            print(f"Excepción genérica: {type(e).__name__}: {str(e)}")
            return 500, {"message": f"Error interno del servidor: {str(e)}"}
    
    @route.post(
        "/refresh-token", 
        response=schema.TokenRefreshOutputSchema, 
        url_name="refresh",
        auth=None
    )
    def refresh_token(self, refresh_token: schema.TokenRefreshSchema):
        """Refresh JWT token"""
        refresh = schema.TokenRefreshOutputSchema(**refresh_token.dict())
        return refresh
