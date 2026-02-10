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
)

from apps.administracion.models.tipo_concreto        import TipoConcreto

@admin.register(TipoConcreto)
class TipoConcretoAdmin(ModelAdmin):
    list_per_page = 10

    

    def editar(self, obj):
        return format_html('<a class="btn" href="/admin/administracion/tipoconcreto/{}/change/"><span class="material-symbols-outlined text-primary-600 dark:text-primary-600">edit</span></a>', obj.id)
    def eliminar(self, obj):
        return format_html('<a class="btn" href="/admin/administracion/tipoconcreto/{}/delete/"><span class="material-symbols-outlined text-red-600 dark:text-red-600">delete</span></a>', obj.id)


    list_display        = ('nombre', 'editar','eliminar')
    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True
    ordering = ['nombre']