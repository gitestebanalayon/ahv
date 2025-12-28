from django.contrib import admin
from django.contrib import messages
from django.utils.translation import ngettext
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _

from apps.cuenta.models import User
from django.contrib.auth.admin import UserAdmin

from unfold.decorators import action
from unfold.forms import AdminPasswordChangeForm, UserCreationForm
from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import (
    TextFilter,
    BooleanRadioFilter,
)

class UsuarioFilter(TextFilter):
    title = _("usuario")
    parameter_name = "username"

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(username=self.value())
        return queryset


class CedulaFilter(TextFilter):
    title = _("cedula")
    parameter_name = "cedula"

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(cedula=self.value())
        return queryset


class CorreoFilter(TextFilter):
    title = _("correo")
    parameter_name = "email"

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(email=self.value())
        return queryset


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email',)


@admin.register(User)
class CustomUserAdmin(UserAdmin, ModelAdmin):
    list_filter_sheet = False
    list_filter_position = "top"
    list_filter_submit = True
    
    def editar(self, obj):
        return format_html(
            '<a class="btn btn-link" href="/admin/cuenta/user/{}/change/">'
            '<span class="material-symbols-outlined">edit</span>'
            '</a>', 
            obj.id
        )
    editar.short_description = ""
        
    def eliminar(self, obj):
        # Si el usuario es superusuario, no mostrar enlace de eliminación
        if obj.is_superuser:
            return format_html('')
        return format_html(
            '<a class="btn btn-link" href="/admin/cuenta/user/{}/delete/">'
            '<span class="material-symbols-outlined">delete</span>'
            '</a>', 
            obj.id
        )
    eliminar.short_description = ""
        
    @admin.action(permissions=["change"])
    def desactivar(self, request, queryset):
        # No permitir desactivar superusuarios
        queryset = queryset.filter(is_superuser=False)
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

    prepopulate_fields = {'username': ('origen', 'cedula', 'email',)}
    
    add_form = CustomUserCreationForm
    change_password_form = AdminPasswordChangeForm
    
    # Campos que se mostrarán en la lista
    list_display = ('username', 'cedula', 'email', 'editar', 'eliminar')
    list_display_links = None
    actions = ['desactivar', 'activar']
    
    # Filtros
    list_filter = [
        # UsuarioFilter,
        # CedulaFilter,
        # CorreoFilter,
        # ("is_active", BooleanRadioFilter),
        # ("is_staff", BooleanRadioFilter),
    ]
    
    # Campos de búsqueda (opcional)
    search_fields = ['username', 'cedula', 'email']
    
    # Ordenamiento
    ordering = ['username', 'cedula', 'email']
    
    # Configuración de los formularios de edición y creación
    fieldsets = [
        (
            ("Credenciales"), 
            {
                "classes":  ["tab"],
                "fields":   ['username','origen','cedula','nombre_apellido','email','password'],
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
                'fields': ('username','origen','cedula','nombre_apellido','email','password1','password2')
            }
        ),
    )

    # Sobrescribir el método para eliminar, para evitar que se eliminen superusuarios
    def delete_model(self, request, obj):
        if obj.is_superuser:
            messages.error(request, "No se puede eliminar un superusuario.")
            return
        super().delete_model(request, obj)

    # Sobrescribir el método para eliminar múltiples usuarios, para evitar eliminar superusuarios
    def delete_queryset(self, request, queryset):
        # Filtrar los superusuarios del queryset
        superusers = queryset.filter(is_superuser=True)
        if superusers.exists():
            messages.error(request, "No se pueden eliminar superusuarios.")
            queryset = queryset.filter(is_superuser=False)
        super().delete_queryset(request, queryset)