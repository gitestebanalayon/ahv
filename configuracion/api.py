from ninja_extra                                import NinjaExtraAPI


from apps.frontend.views                        import router as servicio_router

from apps.cuenta.views.profile                  import router as profile_router
from apps.cuenta.views.change_email             import router as change_email_router
from apps.cuenta.views.change_question_answer   import router as change_question_answer_router
from apps.cuenta.views.create_account           import router as create_account_router
from apps.cuenta.views.change_password          import router as change_password_router

from apps.cuenta.views.create_account           import CreateUserController
from apps.cuenta.views.login                    import MyTokenObtainPairController

api = NinjaExtraAPI(
                        title           = "AHV",
                        description     = "API de AHV",
                        urls_namespace  = "demostrador",
                    )



api.add_router("/servicio/",    servicio_router)

api.add_router("/auth/",        change_password_router)
api.add_router("/auth/",        change_email_router)
api.add_router("/auth/",        change_question_answer_router)
api.add_router("/auth/",        create_account_router)
api.add_router("/auth/",        profile_router)


api.register_controllers(CreateUserController)
api.register_controllers(MyTokenObtainPairController)