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

from apps.sistema.models.vehiculo        import Vehiculo


class FiltroNombre(TextFilter):
    title = _("Nombre")
    parameter_name = "nombre"

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(nombre = self.value())
        return queryset

@admin.register(Vehiculo)
class VehiculoAdmin(ModelAdmin):

    def editar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/vehiculo/{}/change/"><span class="material-symbols-outlined text-blue-700 dark:text-blue-200">edit</span></a>', obj.id)
    def eliminar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/vehiculo/{}/delete/"><span class="material-symbols-outlined text-red-700 dark:text-red-200">delete</span></a>', obj.id)

    def estado_vehiculo(self, obj):
        return format_html('<span class="inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-200">{}</span>', obj.estado_vehiculo_nombre)
    
   
    list_display        = ('matricula', 'alias' ,'estado_vehiculo','editar','eliminar')
    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True