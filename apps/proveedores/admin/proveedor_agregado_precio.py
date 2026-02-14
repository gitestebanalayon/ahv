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

from apps.proveedores.models.proveedor_agregado_precio        import ProveedorAgregadoPrecio

@admin.register(ProveedorAgregadoPrecio)
class ProveedorAgregadoPrecioAdmin(ModelAdmin):
    list_per_page = 10
    
    def editar(self, obj):
        if self.has_change_permission(self.request, obj=obj):
            return format_html('<a class="btn" href="/admin/proveedores/agregadoprecio/{}/change/"><span class="material-symbols-outlined text-primary-600 dark:text-primary-600">edit</span></a>', obj.id)
        return ""  # Retornar vacío si no tiene permiso
    editar.short_description = ''  # Esto oculta el encabezado de la columna

    def eliminar(self, obj):
        if self.has_delete_permission(self.request, obj=obj):
            return format_html('<a class="btn" href="/admin/proveedores/agregadoprecio/{}/delete/"><span class="material-symbols-outlined text-red-600 dark:text-red-600">delete</span></a>', obj.id)
        return ""  # Retornar vacío si no tiene permiso
    eliminar.short_description = ''  # Esto oculta el encabezado de la columna

     # Sobrescribir el método para obtener list_display dinámicamente
    def get_list_display(self, request):
        # Lista base de columnas
        base_columns = ['proveedor', 'agregado', 'precio', 'fecha_inicio', 'fecha_fin']
        
        # Agregar columnas dinámicamente según permisos
        if request.user.has_perm('proveedores.change_proveedoragregadoprecio'):
            base_columns.append('editar')
        
        if request.user.has_perm('proveedores.delete_proveedoragregadoprecio'):
            base_columns.append('eliminar')
            
        return base_columns

    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True
    ordering = ['-fecha_fin', 'proveedor', 'agregado']

    list_filter_submit = True
    list_filter = [
        ('proveedor', RelatedDropdownFilter),
        ('agregado', RelatedDropdownFilter),
    ]

    fieldsets = [
        (
            ("Precios"), 
            {
                "classes":  ["tab"],
                "fields":   ['proveedor', 'agregado', 'precio'],
            }
        ),
    ]
