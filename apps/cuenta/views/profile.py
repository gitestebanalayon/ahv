from django.shortcuts           import get_object_or_404

from ninja                      import Router
from ninja_jwt.authentication   import AsyncJWTAuth


from apps.cuenta.models         import User as Model
from apps.cuenta.schemes.token  import UserSchema

router = Router()
tag = ['auth']

@router.get('/profile/{id}/', tags = tag, response = {200: UserSchema}, auth=AsyncJWTAuth())
def profile(request, id: int):
        data = get_object_or_404(Model, id = id)
        return data
