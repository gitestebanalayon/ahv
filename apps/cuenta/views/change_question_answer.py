
from django.core.exceptions     import ValidationError

from ninja                      import Router
from ninja_jwt.authentication   import AsyncJWTAuth
from ninja.errors               import ValidationError as NinjaValidationError


from configuracion.schemes      import SucessSchema, ErrorSchema
from apps.cuenta.models         import User as Model
from apps.cuenta.schemes.token  import ChangeQASchema


router = Router()
tag = ['auth']


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
