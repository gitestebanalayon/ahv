from ninja import Schema, Field
from pydantic import EmailStr, field_validator, model_validator
from typing import Type
from enum import Enum

from apps.cuenta.models import User

from apps.cuenta.exceptions.auth import (
    BadRequestException,
)

class TipoDocumentoEnum(str, Enum):
    SSN = "SSN"
    ITIN = "ITIN"

class CreateUserSchema(Schema):
    username: str
    nombre_apellido: str
    tipo_documento: TipoDocumentoEnum
    numero: str
    email: EmailStr
    password: str

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if not v:
            raise ValueError('Usuario: El nombre de usuario no puede estar vacío')
        return v
    
    @field_validator('nombre_apellido')
    @classmethod
    def validate_nombre_apellido(cls, v):
        if not v:
            raise ValueError('Nombre y Apellido: El nombre y apellido no puede estar vacío')
        return v

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v:
            raise ValueError('Correo: El correo no puede estar vacío')
        return v

    @field_validator('tipo_documento')
    @classmethod
    def validate_tipo_documento(cls, v):
        if not v:
            raise ValueError('Tipo de documento: El tipo de documento no puede estar vacío')
        
        if v not in ['SSN', 'ITIN']:
            raise ValueError('Tipo de documento: Las opciones válidas son SSN o ITIN')

        return v

    @field_validator('numero')
    @classmethod
    def validate_numero(cls, v):
        if not v:
            raise ValueError('Número: El número de documento no puede estar vacío')
        
        try:
            numero_int = int(v)
            if numero_int <= 0:
                raise ValueError('Número: El número de documento debe ser un número positivo')
        except ValueError:
            raise ValueError('Número: El número de documento debe ser un número válido')
        
        return numero_int

    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not v:
            raise ValueError('Clave: La clave no puede estar vacía')
        
        # Validar longitud de la contraseña (3 a 8 caracteres)
        if len(v) < 3:
            raise ValueError('Clave: La contraseña debe tener al menos 3 caracteres')
        
        if len(v) > 8:
            raise ValueError('Clave: La contraseña no puede tener más de 8 caracteres')
            
        return v

    def create(self) -> Type[User]:
        """Crear usuario en el sistema con validaciones de unicidad"""
        
        # Validaciones de unicidad con el sistema_id del token
        if User.objects.filter(username=self.username).exists():
            raise BadRequestException('Este nombre de usuario ya está registrado en sistema')
        
        numero_int = int(self.numero) if isinstance(self.numero, str) else self.numero
        if User.objects.filter(tipo_documento=self.tipo_documento, numero=numero_int).exists():
            raise BadRequestException('El tipo de documento y el nro. de documento ya está registrado en sistema')
        
        if User.objects.filter(email__iexact=self.email).exists():
            raise BadRequestException('Este correo electrónico ya está registrado en sistema')
        
        # Crear usuario
        return User.objects.create_user(
            username=self.username,
            nombre_apellido=self.nombre_apellido,
            email=self.email,
            tipo_documento=self.tipo_documento,
            numero=numero_int,
            password=self.password,
        )

class UpdatePasswordSchema(Schema):
    old_password: str
    new_password: str

    @field_validator('old_password')
    @classmethod
    def validate_old_password(cls, v):
        if not v:
            raise ValueError('La contraseña actual es requerida')
        return v

    @field_validator('new_password')
    @classmethod
    def validate_new_password(cls, v):
        if not v:
            raise ValueError('La nueva contraseña es requerida')
        
        if len(v) < 3:
            raise ValueError('La nueva contraseña debe tener al menos 3 caracteres')
        
        if len(v) > 8:
            raise ValueError('La nueva contraseña no puede tener más de 8 caracteres')
            
        return v

class UpdateEmailSchema(Schema):
    email: str  # Cambiamos de EmailStr a str para validar manualmente

    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        if not v:
            raise ValueError('El correo es obligatorio')  # 422
        
        # Validar formato de email manualmente
        from pydantic import EmailStr
        try:
            # Verificar si es un email válido
            EmailStr._validate(v)
        except ValueError:
            raise ValueError('El correo electrónico no tiene un formato válido')  # 422
        
        # Validar unicidad (400)
        if User.objects.filter(email__iexact=v).exists():
            raise BadRequestException('Este correo ya está registrado')
        
        return v

class UpdateQASchema(Schema):
    pregunta_01: str
    pregunta_02: str
    pregunta_03: str
    respuesta_01: str
    respuesta_02: str
    respuesta_03: str

    @field_validator('pregunta_01')
    @classmethod
    def validate_pregunta_01(cls, v):
        if not v:
            raise ValueError('La Pregunta 01 no puede estar vacía')  # 422
        return v

    @field_validator('pregunta_02')
    @classmethod
    def validate_pregunta_02(cls, v):
        if not v:
            raise ValueError('La Pregunta 02 no puede estar vacía')  # 422
        return v

    @field_validator('pregunta_03')
    @classmethod
    def validate_pregunta_03(cls, v):
        if not v:
            raise ValueError('La Pregunta 03 no puede estar vacía')  # 422
        return v

    @field_validator('respuesta_01')
    @classmethod
    def validate_respuesta_01(cls, v):
        if not v:
            raise ValueError('La Respuesta 01 no puede estar vacía')  # 422
        return v

    @field_validator('respuesta_02')
    @classmethod
    def validate_respuesta_02(cls, v):
        if not v:
            raise ValueError('La Respuesta 02 no puede estar vacía')  # 422
        return v

    @field_validator('respuesta_03')
    @classmethod
    def validate_respuesta_03(cls, v):
        if not v:
            raise ValueError('La Respuesta 03 no puede estar vacía')  # 422
        return v

    @model_validator(mode='after')
    def validate_unique_questions(self):
        """Validar que las preguntas no se repitan"""
        preguntas = [
            self.pregunta_01.strip().lower(),
            self.pregunta_02.strip().lower(), 
            self.pregunta_03.strip().lower()
        ]
        
        # Verificar si hay preguntas duplicadas
        preguntas_unicas = set()
        preguntas_duplicadas = []
        
        for i, pregunta in enumerate(preguntas, 1):
            if pregunta in preguntas_unicas:
                preguntas_duplicadas.append(f"Pregunta {i}")
            preguntas_unicas.add(pregunta)
        
        if preguntas_duplicadas:
            raise BadRequestException('No se pueden repetir las mismas preguntas')
        
        return self