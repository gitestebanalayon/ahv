from django.shortcuts   import redirect
from ninja              import Router
from ninja.security     import HttpBearer


tag     = ['servicio']
router  = Router()

class AuthBearer(HttpBearer):
    def authenticate(self, request, token):
        if token == "django-insecure-lnn6e++0epb6(s(b@(ig220_#njf=8%wus+dt)v=_x4i2*n&q-":
            return token
        
def inicio(request):
    return redirect('/admin')


@router.get("/estado/", tags = tag, auth=AuthBearer())
def comprobar_servicio(request):
    return 200


import json
from django.shortcuts import render

def debug_view(request):
    test_data = {
        'titulo_operativo': 'Operativo de Prueba',
        'total_participantes': 42,
        'mensaje': '¡Funciona!'
    }
    
    return render(request, 'frontend/debug_section.html', {
        'verbose_name': 'Vista de Prueba',
        'debug_data': test_data,
        'debug_data_json': json.dumps(test_data),
        'instance': type('Obj', (object,), {'titulo': 'Test Object'})()
    })