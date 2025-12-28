from datetime                   import datetime

from ninja_extra                import api_controller, route
from ninja_jwt                  import schema
from ninja_jwt.authentication   import JWTAuth
from ninja_jwt.controller       import TokenObtainSlidingController
from ninja_jwt.tokens           import SlidingToken

from apps.cuenta.schemes.crear_cuenta   import (CreateUserSchema, UserTokenOutSchema,)
from configuracion.schemes              import ErrorSchema, SucessSchema


@api_controller("/auth", tags = ["auth"], auth = JWTAuth())
class UserController:
    @route.post("/create", response = {201: UserTokenOutSchema}, url_name = "user-create", auth = None)
    def create_user(self, user_schema: CreateUserSchema):
        user    = user_schema.create()
        token   = SlidingToken.for_user(user)
        #return UserTokenOutSchema(user = user, token = str(token), token_exp_date = datetime.utcfromtimestamp(token["exp"]))
        return UserTokenOutSchema(user = user, token = str(token))
        

@api_controller("/auth", tags=["auth"])
class UserTokenController(TokenObtainSlidingController):
    auto_import = True

    @route.post("/login", response = {200: UserTokenOutSchema, 404: ErrorSchema}, url_name = "login")
    def obtain_token(self, user_token: schema.TokenObtainSlidingSerializer):
        user    = user_token._user
        token   = SlidingToken.for_user(user)
        #return UserTokenOutSchema(user = user, token = str(token), token_exp_date = datetime.utcfromtimestamp(token["exp"]))
        return UserTokenOutSchema(user = user, token = str(token))

    @route.post("/refresh", response = schema.TokenRefreshSlidingSerializer, url_name = "refresh")
    def refresh_token(self, refresh_token: schema.TokenRefreshSlidingSchema):
        refresh = schema.TokenRefreshSlidingSerializer(**refresh_token.dict())
        return refresh

    @route.post("/exit", response = {200: SucessSchema}, url_name = "exit")
    def exit(self, refresh_token: schema.TokenRefreshSlidingSchema):
        refresh = schema.TokenRefreshSlidingSerializer(**refresh_token.dict())
        return 200, {"message": "OK"}