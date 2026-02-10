from django.contrib                 import admin, messages
from django.utils.translation       import ngettext, gettext_lazy as _
from django.utils.html              import format_html
from django.utils.http              import urlencode
from django.urls                    import reverse

from unfold.admin                   import ModelAdmin
from unfold.sections                import TemplateSection
from unfold.contrib.filters.admin   import (
    TextFilter,
    BooleanRadioFilter,
    ChoicesRadioFilter,
    ChoicesCheckboxFilter,
    FieldTextFilter,
    ChoicesDropdownFilter,
    MultipleChoicesDropdownFilter,
    RelatedDropdownFilter,
    MultipleRelatedDropdownFilter,
    DropdownFilter,
    MultipleDropdownFilter
)

from apps.administracion.models.tipo_concreto_precio        import TipoConcretoPrecio

@admin.register(TipoConcretoPrecio)
class TipoConcretoPrecioAdmin(ModelAdmin):
    list_per_page = 10
    

    def editar(self, obj):
        if self.has_change_permission(self.request, obj=obj):
            return format_html('<a class="btn" href="/admin/administracion/tipoconcretoprecio/{}/change/"><span class="material-symbols-outlined text-primary-600 dark:text-primary-600">edit</span></a>', obj.id)
        return ""  # Retornar vacío si no tiene permiso
    editar.short_description = ''  # Esto oculta el encabezado de la columna

    def eliminar(self, obj):
        if self.has_delete_permission(self.request, obj=obj):
            return format_html('<a class="btn" href="/admin/administracion/tipoconcretoprecio/{}/delete/"><span class="material-symbols-outlined text-red-600 dark:text-red-600">delete</span></a>', obj.id)
        return ""  # Retornar vacío si no tiene permiso
    eliminar.short_description = ''  # Esto oculta el encabezado de la columna

     # Sobrescribir el método para obtener list_display dinámicamente
    def get_list_display(self, request):
        # Lista base de columnas
        base_columns = ['tipo_concreto', 'precio', 'fecha_inicio', 'fecha_fin']
        
        # Agregar columnas dinámicamente según permisos
        if request.user.has_perm('administracion.change_tipoconcretoprecio'):
            base_columns.append('editar')
        
        if request.user.has_perm('administracion.delete_tipoconcretoprecio'):
            base_columns.append('eliminar')
            
        return base_columns

    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True
    ordering = ['-fecha_fin', 'tipo_concreto']

    list_filter_submit = True
    list_filter = [
        ('tipo_concreto', RelatedDropdownFilter),
    ]

    