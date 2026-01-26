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

from apps.administracion.models.precio_rango_pedido        import PrecioRangoPedido

@admin.register(PrecioRangoPedido)
class PrecioRangoPedidoAdmin(ModelAdmin):
    list_per_page = 10

    def editar(self, obj):
        if self.has_change_permission(self.request, obj=obj):
            return format_html(
                '<a class="btn" href="/admin/administracion/preciorangopedido/{}/change/">'
                '<span class="material-symbols-outlined text-blue-700 dark:text-blue-200">edit</span>'
                '</a>', 
                obj.id
            )
        return ""  # Retornar vacío si no tiene permiso
        
    editar.short_description = ''  # Esto oculta el encabezado de la columna
    editar.allow_tags = True  # Permite renderizar HTML en la columna
    
    def eliminar(self, obj):
        if self.has_delete_permission(self.request, obj=obj):
            return format_html(
                '<a class="btn" href="/admin/administracion/preciorangopedido/{}/delete/">'
                '<span class="material-symbols-outlined text-red-700 dark:text-red-200">delete</span>'
                '</a>', 
                obj.id
            )
        return ""
    eliminar.short_description = ''  # Esto oculta el encabezado de la columna
    eliminar.allow_tags = True
        
  


    def rango_pedido_str(self, obj):
            if obj.rango_pedido:
                return str(obj.rango_pedido)
            return "-"
    rango_pedido_str.short_description = "Rango"
    rango_pedido_str.admin_order_field = "rango_pedido__nombre"
  
  
    list_display        = ('rango_pedido_str', 'precio_por_yarda', 'fecha_inicio', 'fecha_fin', 'editar','eliminar')
    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True
    
    
    fieldsets = [
        (
            ("Precio de Rango"), 
            {
                "classes":  ["tab"],
                "fields":   ['rango_pedido', 'precio_por_yarda', 'motivo_cambio'],
            }
        ),

    ]