from django.core.exceptions     import ValidationError

from ninja                      import Router
from ninja_jwt.authentication   import JWTAuth
from ninja_extra                import api_controller, route
from ninja.errors               import ValidationError as NinjaValidationError


from configuracion.schemes      import SucessSchema, ErrorSchema
from apps.cuenta.schemes.token  import CreateUserSchema


router = Router()
tag = ['auth']

        
@api_controller("/auth", tags=tag)
class CreateUserController:
    
    @route.post("/create/", response = {201: SucessSchema, 404: ErrorSchema}, url_name = "user-create", auth=JWTAuth)
    def create_user(self, user_schema: CreateUserSchema):
        try:
            user    = user_schema.create()
            return 201, {"message": "Operacion Exitosa"}
        except ValidationError as err:
                raise NinjaValidationError(err.messages)

        except:
            return 204, {"message": "Operacion Fallida"}