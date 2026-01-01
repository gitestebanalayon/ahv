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

from apps.sistema.models.conductor        import Conductor


class FiltroNombre(TextFilter):
    title = _("Nombre")
    parameter_name = "nombre"

    def queryset(self, request, queryset):
        if self.value() is not None:
            return queryset.filter(nombre = self.value())
        return queryset

@admin.register(Conductor)
class ConductorAdmin(ModelAdmin):

    def editar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/conductor/{}/change/"><span class="material-symbols-outlined text-blue-700 dark:text-blue-200">edit</span></a>', obj.id)
    def eliminar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/conductor/{}/delete/"><span class="material-symbols-outlined text-red-700 dark:text-red-200">delete</span></a>', obj.id)

    def estado_conductor(self, obj):
        return format_html('<span class="inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-200">{}</span>', obj.estado_conductor_nombre)
        
    def tiene_vehiculo(self, obj):
        if obj.vehiculo_id:
            return format_html('<div class="inline-flex font-semibold items-center justify-center leading-normal h-6 w-6 rounded-full uppercase whitespace-nowrap bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400"> <span class="material-symbols-outlined">check_small</span> </div>') 
        else:
            return format_html('<div class="inline-flex font-semibold items-center justify-center leading-normal h-6 w-6 rounded-full uppercase whitespace-nowrap bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400"> <span class="material-symbols-outlined">close_small</span> </div>')


    list_display        = ('nombre', 'licencia', 'telefono', 'estado_conductor', 'tiene_vehiculo', 'editar','eliminar')
    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True