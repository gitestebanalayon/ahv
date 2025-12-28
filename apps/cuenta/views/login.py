from ninja                      import Router
from ninja_extra                import api_controller, route
from ninja_jwt.controller       import TokenObtainPairController
from ninja_jwt                  import schema

from apps.cuenta.schemes.token  import MyTokenObtainPairOutSchema, MyTokenObtainPairSchema


router = Router()
tag = ['auth']


@api_controller('/auth', tags=tag)
class MyTokenObtainPairController(TokenObtainPairController):
    @route.post("/login/", response=MyTokenObtainPairOutSchema, url_name="token_obtain_pair")
    def obtain_token(self, user_token: MyTokenObtainPairSchema):
        return user_token.output_schema()
    
    @route.post("/refresh/", response = schema.TokenRefreshOutputSchema, url_name = "refresh")
    def refresh_token(self, refresh_token: schema.TokenObtainPairOutputSchema):
        refresh = schema.TokenRefreshOutputSchema(**refresh_token.dict())
        return refresh