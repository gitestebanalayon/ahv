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

from apps.auxiliares.models.estado_vehiculo        import EstadoVehiculo


class FiltroNombre(TextFilter):
    title = _("Nombre")
    parameter_name = "nombre"

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(nombre = self.value())
        return queryset

@admin.register(EstadoVehiculo)
class EstadoVehiculoAdmin(ModelAdmin):

    def editar(self, obj):
        return format_html('<a class="btn" href="/admin/auxiliares/estadovehiculo/{}/change/"><span class="material-symbols-outlined">edit</span></a>', obj.id)

    def eliminar(self, obj):
        return format_html('<a class="btn" href="/admin/auxiliares/estadovehiculo/{}/delete/"><span class="material-symbols-outlined">delete</span></a>', obj.id)


    # @admin.action(permissions  = ["change"])
    # def editar1(self, obj):
    #     return format_html('<a class="btn" href="/admin/auxiliares/estado_vehiculo/{}/change/">'
    #     '<span class="inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap bg-blue-100 text-blue-700 dark:bg-blue-500/20 dark:text-blue-400">' \
    #     'Editar'
    #     '</span>'
    #     '</a>', obj.id)
    
    # @admin.action(permissions  = ["delete"])
    # def eliminar1(self, obj):
    #     return format_html('<a class="btn" href="/admin/auxiliares/estado_vehiculo/{}/delete/">'
    #     '<span class="inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400">' \
    #     'Eliminar'
    #     '</span>'
    #     '</a>', obj.id)


    list_display        = ('nombre','is_delete','editar','eliminar')
    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True