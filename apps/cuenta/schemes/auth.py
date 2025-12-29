from ninja_schema import ModelSchema, Schema
from ninja import Schema
from ninja_extra.exceptions import APIException
from pydantic import field_validator
from typing import List, Optional
from django.contrib.auth.models import Group
from apps.cuenta.models import User

from apps.cuenta.tokens import CustomAccessToken, CustomRefreshToken
from apps.cuenta.exceptions.auth import (
    UserNotFoundInSystemException,
    InvalidPasswordException
)

class GroupSchema(ModelSchema):
    class Config:
        model = Group
        include = ("id", "name",)

class UserSchema(ModelSchema):
    groups: List[GroupSchema] = []  # Array vacío por defecto

    class Config:
        model = User
        include = (
            "id",
            "username", 
            "tipo_documento",
            "numero",
            "email",
            "is_superuser",
        )

class MyTokenObtainPairOutSchema(Schema):
    refresh: str
    access: str
    user: UserSchema
    is_root: bool = False  # ✅ Agregar flag para root

class MyTokenObtainPairInputSchema(Schema):
    username: str
    password: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v:
            raise ValueError('Usuario: El nombre de usuario es obligatorio')
        return v

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v:
            raise ValueError('Contraseña: La contraseña es obligatoria')
        return v

class MyTokenObtainPairSchema:
    def __init__(self, input_schema: MyTokenObtainPairInputSchema):
        self.input_schema = input_schema
        self.user = None

    def authenticate(self):
        """Autenticar usuario por username con caso especial para root"""
        try:
            user = User.objects.get(username=self.input_schema.username)
            
            if not user.check_password(self.input_schema.password):
                raise InvalidPasswordException()
            
            print(user)
            
            if user:
                self.user = user
                return True
            else:
                raise UserNotFoundInSystemException()
                
        except User.DoesNotExist:
            raise UserNotFoundInSystemException()

    def get_tokens(self):
        """Generar tokens JWT personalizados con TODOS los permisos"""
        if not self.user:
            raise APIException("Usuario no autenticado")
        
        refresh = CustomRefreshToken.for_user(self.user)
        access = CustomAccessToken.for_user(self.user)
        

        
        # Obtener nombres de grupos del usuario
        user_groups = [group.name for group in self.user.groups.all()]
        
        if self.user.is_superuser is None:
            is_root = True
        else:
            is_root = False
        
        access['groups'] = user_groups
        access['is_root'] = is_root  # ✅ Flag para identificar root
        
        refresh['groups'] = user_groups
        refresh['is_root'] = is_root
        
        return {
            "refresh": str(refresh),
            "access": str(access),
            "user": UserSchema.from_orm(self.user),
            "is_root": is_root  # ✅ También en la respuesta directa
        }

    def output_schema(self):
        """Retornar schema de respuesta"""
        try:
            self.authenticate()
            tokens = self.get_tokens()
            
            user_data = UserSchema.from_orm(self.user)
            
            return MyTokenObtainPairOutSchema(
                refresh=tokens["refresh"],
                access=tokens["access"],
                user=user_data,
                is_root=tokens["is_root"]  # ✅ Incluir flag en la respuesta
            )
            
        except (InvalidPasswordException, UserNotFoundInSystemException) as e:
            raise e
        except Exception as e:
            raise APIException(f"Error interno del servidor: {str(e)}")
