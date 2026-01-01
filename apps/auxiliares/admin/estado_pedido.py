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

from apps.auxiliares.models.estado_pedido        import EstadoPedido


class FiltroNombre(TextFilter):
    title = _("Nombre")
    parameter_name = "nombre"

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(nombre = self.value())
        return queryset

@admin.register(EstadoPedido)
class EstadoPedidoAdmin(ModelAdmin):

    def editar(self, obj):
        return format_html('<a class="btn" href="/admin/auxiliares/estadopedido/{}/change/"><span class="material-symbols-outlined">edit</span></a>', obj.id)
    def eliminar(self, obj):
        return format_html('<a class="btn" href="/admin/auxiliares/estadopedido/{}/delete/"><span class="material-symbols-outlined">delete</span></a>', obj.id)


    list_display        = ('nombre','estatus','editar','eliminar')
    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True