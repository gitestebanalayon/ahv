from django.db                          import models
from django.contrib.auth.models         import (AbstractBaseUser, BaseUserManager, PermissionsMixin)
# from simple_history.models              import HistoricalRecords


class UserManager(BaseUserManager):

    def create_user(self, username, email, origen, cedula, nombre_apellido, password = None):
        user = self.model(
                            username        = username,
                            email           = self.normalize_email(email),
                            origen          = origen,
                            cedula          = cedula,
                            nombre_apellido = nombre_apellido,
                            )
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, username, email, origen, cedula, nombre_apellido, password = None):
        user                = self.create_user(username, email, origen, cedula, nombre_apellido, password)
        user.is_superuser   = True
        user.is_staff       = True
        user.save()
        return user


class User(AbstractBaseUser, PermissionsMixin):
    V    =   'V'
    E    =   'E'

    ORIGEN  =   (
                    (V,  'V'),
                    (E,  'E'),
                )

    username                = models.CharField('Usuario',                   max_length =  20,   unique = True,                              )
    email                   = models.EmailField('Correo',                   max_length = 255,   unique = True                               )
    origen                  = models.CharField('Origen',                    max_length =   1,   choices = ORIGEN                            )
    cedula                  = models.IntegerField('Cédula',                                                                                 )
    nombre_apellido         = models.CharField('Nom/Ape',                   max_length = 255,                   blank = True, null = True   )
    pregunta_01             = models.CharField('Preg. 01',                  max_length = 255,   default = 'INDETERMINADA'                   )
    pregunta_02             = models.CharField('Preg. 02',                  max_length = 255,   default = 'INDETERMINADA'                   )
    pregunta_03             = models.CharField('Preg. 03',                  max_length = 255,   default = 'INDETERMINADA'                   )
    respuesta_01            = models.CharField('Resp. 01',                  max_length = 255,   default = 'INDETERMINADA'                   )
    respuesta_02            = models.CharField('Resp. 02',                  max_length = 255,   default = 'INDETERMINADA'                   )
    respuesta_03            = models.CharField('Resp. 03',                  max_length = 255,   default = 'INDETERMINADA'                   )
    fecha_registro          = models.DateTimeField('Fecha Registro',        auto_now_add = True                                             )
    #fecha_actualizacion     = models.DateTimeField('Fecha Actualización',   auto_now = True                                                 )
    is_verified             = models.BooleanField('VERIFICADO',                                  default = True                             )
    is_active               = models.BooleanField('Esta Activo',                                 default = True                             )
    is_staff                = models.BooleanField('Personal de Confianza',                       default = False                            )
    is_superuser            = models.BooleanField('Es ROOT',                                     default = False                            )
    #historical              = HistoricalRecords()
    objects                 = UserManager()

    class Meta:
        managed             = True
        db_table            = 'cuenta\".\"usuario'
        verbose_name        = 'Usuario'
        verbose_name_plural = 'Usuarios'
        unique_together     = ('origen','cedula')

    USERNAME_FIELD  = 'username'
    REQUIRED_FIELDS = ['origen','cedula','nombre_apellido','email']

    def __str__(self):
        return self.username