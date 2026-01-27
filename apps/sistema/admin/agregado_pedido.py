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

from apps.sistema.models.agregado_pedido        import AgregadoPedido



@admin.register(AgregadoPedido)
class AgregadoPedidoAdmin(ModelAdmin):
    list_per_page = 10

    def editar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/agregadopedido/{}/change/"><span class="material-symbols-outlined text-blue-700 dark:text-blue-200">edit</span></a>', obj.id)
    def eliminar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/agregadopedido/{}/delete/"><span class="material-symbols-outlined text-red-700 dark:text-red-200">delete</span></a>', obj.id)

    def agregado_nombre(self, obj):
        return obj.agregado.nombre if obj.agregado else '-'
    
    def numero_orden(self, obj):
        return obj.pedido.codigo_pedido if obj.pedido else '-'
    
  
    list_display        = ('agregado_nombre' , 'numero_orden', 'editar','eliminar')
    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True