from django.core.exceptions     import ValidationError
from django.shortcuts           import get_object_or_404

from ninja_jwt.controller       import TokenObtainPairController
from ninja_jwt.authentication   import AsyncJWTAuth
from ninja_jwt.authentication   import JWTAuth
from ninja_jwt                  import schema

from ninja_extra                import api_controller, route

from ninja                      import Router
from ninja.security             import HttpBearer
from ninja.errors               import ValidationError as NinjaValidationError


from configuracion.schemes      import SucessSchema, ErrorSchema
from apps.cuenta.models         import User as Model
from apps.cuenta.schemes.token  import MyTokenObtainPairOutSchema, MyTokenObtainPairSchema
from apps.cuenta.schemes.token  import CreateUserSchema, ChangePasswordSchema, ChangeEmailSchema, ChangeQASchema, UserSchema


router = Router()
tag = ['Auth']

        
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


@api_controller('/auth', tags=tag)
class MyTokenObtainPairController(TokenObtainPairController):
    @route.post("/login/", response=MyTokenObtainPairOutSchema, url_name="token_obtain_pair")
    def obtain_token(self, user_token: MyTokenObtainPairSchema):
        return user_token.output_schema()
    
    @route.post("/refresh/", response = schema.TokenRefreshOutputSchema, url_name = "refresh")
    def refresh_token(self, refresh_token: schema.TokenObtainPairOutputSchema):
        refresh = schema.TokenRefreshOutputSchema(**refresh_token.dict())
        return refresh


@router.post('/change-password/', tags=tag, response = {200: SucessSchema, 400: ErrorSchema}, auth=AsyncJWTAuth())
def change_password(request, payload: ChangePasswordSchema):
    user_id         = payload.user_id
    old_password    = payload.old_password
    new_password    = payload.new_password

    model = Model.objects.get(id=user_id)

    if model.check_password(old_password):
        model.set_password(new_password)
        model.save()
        return 200, {"message": "Operación Exitosa"}
    else:
        return 400, {"message": "Operación Fallida"}


@router.put('/change-email/{id}/', tags=tag, response={200: SucessSchema, 404: ErrorSchema}, auth=AsyncJWTAuth())
def change_email(request, id: int, payload: ChangeEmailSchema):
    try:
        model = Model.objects.get(id=id)
        
        for attr, value in payload.dict().items():
            setattr(model, attr, value)
        model.save()
        return 200, {"message": "Operacion Exitosa"}
    
    except Model.DoesNotExist as e:
        return 404, {"message": "Operación Fallida"}
    

@router.put('/change-question-answer/{id}/', tags=tag, response={200: SucessSchema, 404: ErrorSchema}, auth=AsyncJWTAuth())
def change_question_and_answer(request, id: int, payload: ChangeQASchema):
    try:
        model = Model.objects.get(id=id)
        
        for attr, value in payload.dict().items():
            setattr(model, attr, value)
        model.save()
        return 200, {"message": "Operacion Exitosa"}
    
    except ValidationError as err:
            raise NinjaValidationError(err.messages)
    
    except Model.DoesNotExist as e:
        return 404, {"message": "Operación Fallida"}
    

@router.get('/profile/{id}/', tags = tag, response = {200: UserSchema}, auth=AsyncJWTAuth())
def profile(request, id: int):
        data = get_object_or_404(Model, id = id)
        return data
