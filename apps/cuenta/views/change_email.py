from ninja                      import Router
from ninja_jwt.authentication   import AsyncJWTAuth


from configuracion.schemes      import SucessSchema, ErrorSchema
from apps.cuenta.models         import User as Model
from apps.cuenta.schemes.token  import ChangeEmailSchema


router = Router()
tag = ['auth']


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