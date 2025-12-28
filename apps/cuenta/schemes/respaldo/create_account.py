from datetime                   import datetime
from typing                     import List, Optional, Type
from django.contrib.auth.models import Group
from ninja                      import Field
from ninja_extra                import status
from ninja_extra.exceptions     import APIException
from ninja_schema               import ModelSchema, Schema, model_validator

from apps.cuenta.models         import User


class GroupSchema(ModelSchema):
    class Config:
        model   = Group
        include = ("name",)


class CreateUserSchema(ModelSchema):
    # Sobre-escitura del campo origen
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
    def unique_name(cls, value_data):
        if User.objects.filter(username__icontains = value_data).exists():
            raise APIException("Este nombre de usuario ya esta registrado", status_code = status.HTTP_400_BAD_REQUEST)
        return value_data

    @model_validator("email")
    def unique_name(cls, value_data):
        if User.objects.filter(email__icontains = value_data).exists():
            raise APIException("Este correo ya esta registrado", status_code = status.HTTP_400_BAD_REQUEST)
        return value_data

    def create(self) -> Type[User]:
        return User.objects.create_user(**self.dict())


class CreateUserOutSchema(CreateUserSchema):
    token: str

    class Config:
        model   = User
        exclude = ("password",)


class UserRetrieveSchema(ModelSchema):
    groups: List[GroupSchema]

    class Config:
        model   = User
        include =   (
                        "id",
                        "username",
                        "origen",
                        "cedula",
                        "nombre_apellido",
                        "email",
                    )


class UserTokenOutSchema(Schema):
    token:          str
    user:           UserRetrieveSchema
    #token_exp_date: Optional[datetime]