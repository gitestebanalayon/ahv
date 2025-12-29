from ninja_jwt.tokens import Token
from django.conf import settings

class CustomToken(Token):
    @classmethod
    def for_user(cls, user):
        """
        Genera un token para el usuario con información personalizada
        """
        token = cls()
        token[settings.NINJA_JWT['USER_ID_CLAIM']] = str(user.id)
        token['email'] = user.email
        token['numero'] = user.numero
        token['username'] = user.username
        token['tipo_documento'] = user.tipo_documento
        
        # Grupos del usuario
        groups = user.groups.all()
        token['groups'] = [group.id for group in groups]
        
        return token


class CustomAccessToken(CustomToken):
    token_type = "access"
    lifetime = settings.NINJA_JWT['ACCESS_TOKEN_LIFETIME']


class CustomRefreshToken(CustomToken):
    token_type = "refresh"
    lifetime = settings.NINJA_JWT['REFRESH_TOKEN_LIFETIME']