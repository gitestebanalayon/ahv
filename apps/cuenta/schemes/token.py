from ninja_jwt.schema           import TokenObtainPairInputSchema
from ninja_jwt.tokens           import RefreshToken
from ninja_schema               import ModelSchema, Schema, model_validator
from ninja                      import Schema, Field
from ninja_extra.exceptions     import APIException
from pydantic                   import EmailStr


from typing                     import Type, Dict,List
from django.contrib.auth.models import Group
from apps.cuenta.models         import User


class GroupSchema(ModelSchema):
    class Config:
        model   =   Group
        include =   ("name",)


class UserSchema(ModelSchema):
    groups: List[GroupSchema]
    origen: str = Field(alias="origen")

    class Config:
        model   =   User
        include =   (
                        "id",
                        "username",
                        "origen",
                        "cedula",
                        "nombre_apellido",
                        "email",
                        "pregunta_01",
                        "pregunta_02",
                        "pregunta_03",
                        "respuesta_01",
                        "respuesta_02",
                        "respuesta_03",
                    )



class MyTokenObtainPairOutSchema(Schema):
    refresh:        str
    access:         str
    user:           UserSchema


class MyTokenObtainPairSchema(TokenObtainPairInputSchema):
    @classmethod
    def get_response_schema(cls) -> Type[Schema]:
        return MyTokenObtainPairOutSchema

    @classmethod
    def get_token(cls, user) -> Dict:
        values  = {}
        refresh = RefreshToken.for_user(user)
        values["refresh"]   = str(refresh)
        values["access"]    = str(refresh.access_token)
        values.update(user  = UserSchema.from_orm(user))
        return values





class CreateUserSchema(ModelSchema):
    origen: str = Field(alias="origen")

    class Config:
        model   =   User
        include =   [
                        "username",
                        "origen",
                        "cedula",
                        "nombre_apellido",
                        "email",
                        "password",
                    ]

    @model_validator("username")
    def user_null(cls, value_data):
        if value_data == "":
            raise APIException("Usuario: El nombre de usuario no puede estar vacio")
        return value_data

    @model_validator("email")
    def email_null(cls, value_data):
        if value_data == "":
            raise APIException("Correo: El correo no puede estar vacio")
        return value_data

    @model_validator("origen")
    def origen_null(cls, value_data):
        if value_data == "":
            raise APIException("Origen: El origen no puede estar vacio")
        return value_data

    @model_validator("cedula")
    def cedula_null(cls, value_data):
        if value_data == "":
            raise APIException("Cedula: El número de cédula no puede estar vacio")
        return value_data

    @model_validator("nombre_apellido")
    def nombre_apellido_null(cls, value_data):
        if value_data == "":
            raise APIException("Nombre Apellido: El nombre y apellido no puede estar vacio")
        return value_data
    
    @model_validator("password")
    def password_null(cls, value_data):
        if value_data == "":
            raise APIException("Clave: la clave no puede estar vacia")
        return value_data




    @model_validator("username")
    def unique_username(cls, value_data):
        if User.objects.filter(username = value_data).exists():
            raise APIException("Usuario: Este nombre de usuario ya esta registrado")
        return value_data

    @model_validator("email")
    def unique_email(cls, value_data):
        if User.objects.filter(email__icontains = value_data).exists():
            raise APIException("Correo: Este correo ya esta registrado")
        return value_data

    @model_validator("origen")
    def origen_validate(cls, value_data):
        if value_data == 'V' or value_data == 'E':
            return value_data
        raise APIException("Origen: Las opciones validad son V o E")
        
    @model_validator("cedula")
    def unique_cedula(cls, value_data):
        if User.objects.filter(origen = 'V', cedula = value_data).exists():
            raise APIException("Cedula: esta Cedula ya esta registrada")
        elif User.objects.filter(origen = 'E', cedula = value_data).exists():
            raise APIException("Cedula: esta Cedula ya esta registrada")
        return value_data

    def create(self) -> Type[User]:
        return User.objects.create_user(**self.dict())


    
class ChangePasswordSchema(Schema):
    user_id:        int
    old_password:   str
    new_password:   str


class ChangeEmailSchema(Schema):
    email: EmailStr
    class Config:
        model   = User
        include = ("email",)
    
    @model_validator("email")
    def emty_email(cls, value_data):
        if value_data == "":
            raise APIException("El correo es obligatorio")
        return value_data

    @model_validator("email")
    def unique_email(cls, value_data):
        if User.objects.filter(email__icontains = value_data).exists():
            raise APIException("Este correo ya esta registrado")
        return value_data
    

class ChangeQASchema(ModelSchema):
    class Config:
        model   =   User
        include =   (
                        "pregunta_01",
                        "pregunta_02",
                        "pregunta_03",
                        "respuesta_01",
                        "respuesta_02",
                        "respuesta_03",
                    )
        
    @model_validator("pregunta_01")
    def pregunta_01_vacia(cls, value_data):
        if value_data == "":
            raise APIException("La Pregunta 01 no puede estar vacia")
        return value_data
    
    @model_validator("pregunta_02")
    def pregunta_02_vacia(cls, value_data):
        if value_data == "":
            raise APIException("La Pregunta 02 no puede estar vacia")
        return value_data

    @model_validator("pregunta_03")
    def pregunta_03_vacia(cls, value_data):
        if value_data == "":
            raise APIException("La Pregunta 03 no puede estar vacia")
        return value_data

    @model_validator("respuesta_01")
    def respuesta_01_vacia(cls, value_data):
        if value_data == "":
            raise APIException("La Respuesta 01 no puede estar vacia")
        return value_data
    
    @model_validator("respuesta_02")
    def respuesta_02_vacia(cls, value_data):
        if value_data == "":
            raise APIException("La Respuesta 02 no puede estar vacia")
        return value_data
    
    @model_validator("respuesta_03")
    def respuesta_03_vacia(cls, value_data):
        if value_data == "":
            raise APIException("La Respuesta 03 no puede estar vacia")
        return value_data