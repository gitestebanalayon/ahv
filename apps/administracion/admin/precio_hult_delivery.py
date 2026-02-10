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

from apps.administracion.models.precio_hult_delivery        import PrecioHultDelivery

@admin.register(PrecioHultDelivery)
class PrecioHultDeliveryAdmin(ModelAdmin):
    list_per_page = 10

    def editar(self, obj):
        if self.has_change_permission(self.request, obj=obj):
            return format_html(
                '<a class="btn" href="/admin/administracion/preciohultdelivery/{}/change/">'
                '<span class="material-symbols-outlined text-primary-600 dark:text-primary-600">edit</span>'
                '</a>', 
                obj.id
            )
        return ""  # Retornar vacío si no tiene permiso
        
    editar.short_description = ''  # Esto oculta el encabezado de la columna
    editar.allow_tags = True  # Permite renderizar HTML en la columna
    
    def eliminar(self, obj):
        if self.has_delete_permission(self.request, obj=obj):
            return format_html(
                '<a class="btn" href="/admin/administracion/preciohultdelivery/{}/delete/">'
                '<span class="material-symbols-outlined text-red-600 dark:text-red-600">delete</span>'
                '</a>', 
                obj.id
            )
        return ""
    eliminar.short_description = ''  # Esto oculta el encabezado de la columna
    eliminar.allow_tags = True
        
  
    def get_list_display(self, request):
        # Lista base de columnas
        base_columns = ['hult_delivery', 'precio', 'fecha_inicio', 'fecha_fin']
        
        # Agregar columnas dinámicamente según permisos
        if request.user.has_perm('administracion.change_preciohultdelivery'):
            base_columns.append('editar')
        
        if request.user.has_perm('administracion.delete_preciohultdelivery'):
            base_columns.append('eliminar')
            
        return base_columns


  
    list_display        = ('hult_delivery', 'precio', 'fecha_inicio', 'fecha_fin', 'editar','eliminar')
    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True
    
    
    fieldsets = [
        (
            ("Precio de Hult Delivery"), 
            {
                "classes":  ["tab"],
                "fields":   ['hult_delivery', 'precio', 'motivo_cambio'],
            }
        ),

    ]