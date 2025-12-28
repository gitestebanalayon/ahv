from ninja                      import Router
from ninja_jwt.authentication   import AsyncJWTAuth

from configuracion.schemes      import SucessSchema, ErrorSchema
from apps.cuenta.models         import User as Model
from apps.cuenta.schemes.token  import ChangePasswordSchema


router = Router()
tag = ['auth']


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