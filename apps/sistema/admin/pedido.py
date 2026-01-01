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

from apps.sistema.models.pedido        import Pedido

@admin.register(Pedido)
class PedidoAdmin(ModelAdmin):

    def editar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/pedido/{}/change/"><span class="material-symbols-outlined text-blue-700 dark:text-blue-200">edit</span></a>', obj.id)
    def eliminar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/pedido/{}/delete/"><span class="material-symbols-outlined text-red-700 dark:text-red-200">delete</span></a>', obj.id)

    def mas_detalles(self, obj):
        return format_html(
            '''
       
            <a href="#" title="Ver detalles" class="btn" 
                    onclick="showPedidoModal(this)"
                    data-id="{}"
                    data-cliente="{}"
                    data-tipo-documento="{}"
                    data-numero="{}"
                    data-conductor="{}"
                    data-vehiculo="{}"
                    data-fecha-entrega="{}"
                    data-hora-entrega="{}"
                    data-direccion="{}"
                    data-estado="{}"
                    data-observacion="{}"
                    data-total-yardas="{}"
                    data-precio-yarda="{}"
                    data-precio-total="{}">
                <span class="material-symbols-outlined">info</span>
            </a>
            
            ''',
            obj.id,
            obj.cliente,
            obj.cliente.tipo_documento,
            obj.cliente.numero,
            obj.conductor if obj.conductor else "Sin asignar",
            obj.vehiculo if obj.vehiculo else "Sin asignar",
            obj.fecha_entrega,
            obj.hora_entrega,
            obj.direccion_entrega,
            obj.estado_pedido_nombre,
            obj.observacion or "",
            obj.total_yardas or "",
            obj.precio_yarda or "",
            obj.precio_total or ""
        )

    def estado_pedido(self, obj):
        return format_html('<span class="inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-200">{}</span>', obj.estado_pedido_nombre)
        
        
    list_display        = ('cliente', 'conductor', 'vehiculo', 'estado_pedido', 'mas_detalles',  'editar','eliminar')
    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True
    readonly_fields    = ('cliente', 'fecha_entrega', 'hora_entrega', 'direccion_entrega')
    
     # Configuración de los formularios de edición y creación
    fieldsets = [
        (
            ("Asignar pedido"), 
            {
                "classes":  ["tab"],
                "fields":   ['conductor','vehiculo','estado_pedido_nombre'],
            }
        ),
        (
            ("Asignar yardas y precios"), 
            {
                "classes":  ["tab"],
                "fields":   ['total_yardas','precio_yarda','precio_total'],
            }
        ),
    ]
    
    class Media:
        js = (
            'admin/js/pedido_modal.js',
            'admin/js/pedido_admin.js',
            'admin/js/pedido_asignacion.js')