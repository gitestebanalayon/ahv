from ninja                      import Router
from apps.cuenta.schemes.token  import ChangePasswordSchema
from configuracion.schemes      import SucessSchema, ErrorSchema
from apps.cuenta.models         import User as Model


router = Router()

@router.post('/change-password/', tags=['Cuenta'], response = {200: SucessSchema, 400: ErrorSchema})
def change_password(request, payload: ChangePasswordSchema):
    test = str(payload) 
    posicion_01, posicion_02, posicion_03 = test.split(' ')

    posicion_1 = posicion_01[8:]
    posicion_2 = posicion_02[14:-1]
    posicion_3 = posicion_03[14:-1]
    
    user_id      = posicion_1
    old_password = posicion_2
    new_password = posicion_3

    model = Model.objects.get(id=user_id)
    
    if model.check_password(old_password):
        model.set_password(new_password)
        model.save()
        return 200, {"message": "Operación Exitosa"}
    else:
        return 400, {"message": "Operación Fallida"}