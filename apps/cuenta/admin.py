from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.cuenta.models import User
from django.contrib.auth.admin import UserAdmin

from unfold.forms import AdminPasswordChangeForm, UserCreationForm
from unfold.admin import ModelAdmin

# Importar la función para obtener el request actual
from apps.cuenta.middleware import get_current_request

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email',)

@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    list_filter_sheet = False
    list_filter_position = "top"
    list_filter_submit = True
    
    # 1. Sobrescribir get_queryset para excluir al superusuario root
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        
        # Si el usuario actual NO es superusuario, excluir a todos los superusuarios
        if not request.user.is_superuser:
            qs = qs.filter(is_superuser=False)
        # Si el usuario actual ES superusuario, excluir solo el usuario root específico
        else:
            # Excluir el usuario root por username
            qs = qs.exclude(username='root')
        return qs
    
    def editar(self, obj):
        return format_html(
            '<a title="Editar" class="btn btn-link" href="/admin/cuenta/user/{}/change/">'
            '<span class="material-symbols-outlined">edit</span>'
            '</a>', 
            obj.id
        )
    editar.short_description = ""
        
    def eliminar(self, obj):
        request = get_current_request()
        
        # Si el usuario es el mismo que el logueado, no mostrar enlace de eliminación
        if request and obj == request.user:
            return format_html(
                '<span title="No te puedes eliminar a ti mismo" class="badge bg-secondary">'
                '<span class="material-symbols-outlined" style="font-size: 16px;">admin_panel_settings</span>'
                '</span>'
            )
        
        # Si el usuario es superusuario, no mostrar enlace de eliminación
        if obj.is_superuser:
            return format_html(
                '<span title="No se puede eliminar a un superusuario" class="badge bg-danger">'
                '<span class="material-symbols-outlined" style="font-size: 16px;">admin_panel_settings</span>'
                '</span>'
            )
        
        return format_html(
            '<a title="Eliminar" class="btn btn-link" href="/admin/cuenta/user/{}/delete/">'
            '<span class="material-symbols-outlined">delete</span>'
            '</a>', 
            obj.id
        )
    eliminar.short_description = ""
        
    @admin.action(permissions=["change"])
    def desactivar(self, request, queryset):
        # No permitir desactivar superusuarios
        queryset = queryset.filter(is_superuser=False)
        # Evitar que el usuario se desactive a sí mismo
        queryset = queryset.exclude(id=request.user.id)
        desactivados = queryset.update(is_active=False)
        self.message_user(request, ngettext(
            "%d Operación Exitosa", 
            "%d Operación Exitosa", 
            desactivados
        ) % desactivados, messages.SUCCESS)

    @admin.action(permissions=["change"])
    def activar(self, request, queryset):
        reactivados = queryset.update(is_active=True)
        self.message_user(request, ngettext(
            "%d Operación Exitosa", 
            "%d Operación Exitosa", 
            reactivados
        ) % reactivados, messages.SUCCESS)

    prepopulate_fields = {'username': ('tipo_documento', 'numero', 'email',)}
    
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    # Campos que se mostrarán en la lista
    list_display = ('username', 'tipo_documento', 'numero', 'email', 'is_active', 'is_staff',  'editar', 'eliminar')
    list_display_links = None
    actions = ['desactivar', 'activar']
    
    # Filtros
    list_filter = []
    
    # Campos de búsqueda (opcional)
    search_fields = ['username', 'numero', 'email']
    
    # Ordenamiento
    ordering = ['username', 'numero', 'email']
    
    # Configuración de los formularios de edición y creación
    fieldsets = [
        (
            ("Credenciales"), 
            {
                "classes":  ["tab"],
                "fields":   ['username','tipo_documento','numero','nombre_apellido','email','password'],
            }
        ),
        (
            ("Permisos"),
            {
                "classes":  ["tab"],
                "fields":   ['is_staff','is_active',],
            },
        ),
        (
            ("Grupos"),
            {
                "classes":  ["tab"],
                "fields":   ['groups',],
            },
        ),
        (
            ("Actividad"),
            {
                "classes":  ["tab"],
                "fields":   ['fecha_registro','last_login',],
            },
        ),
    ]
    
    # Campos que son solo lectura
    readonly_fields = ['pregunta_01','pregunta_02','pregunta_03','respuesta_01','respuesta_02','respuesta_03','last_login','fecha_registro','is_superuser']
    
    # Configuración del formulario para agregar un usuario
    add_fieldsets = (
        (
            None,   {
                'classes': ('wide',),
                'fields': ('username','tipo_documento','numero','nombre_apellido','email','password1','password2')
            }
        ),
    )

    def delete_model(self, request, obj):
        if obj == request.user:
            messages.error(request, "No puedes eliminarte a ti mismo.")
            return
        if obj.is_superuser:
            messages.error(request, "No se puede eliminar un superusuario.")
            return
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        # Excluir al usuario actual del queryset
        queryset = queryset.exclude(id=request.user.id)
        # Filtrar los superusuarios del queryset
        superusers = queryset.filter(is_superuser=True)
        if superusers.exists():
            messages.error(request, "No se pueden eliminar superusuarios.")
            queryset = queryset.filter(is_superuser=False)
        super().delete_queryset(request, queryset)