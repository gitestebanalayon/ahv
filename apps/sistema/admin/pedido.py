from django.contrib                 import admin, messages
from django.utils.translation       import ngettext, gettext_lazy as _
from django.utils.html              import format_html
from django.utils.http              import urlencode
from django.urls                    import reverse

from unfold.admin                   import ModelAdmin
from unfold.paginator               import InfinitePaginator
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

from apps.sistema.models.pedido        import Pedido, Entrega

@admin.register(Pedido)
class PedidoAdmin(ModelAdmin):
     # Cambia esto para mostrar 10 registros por página
    list_per_page = 10
    
  

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
                    data-fecha-entrega="{}"
                    data-hora-entrega="{}"
                    data-direccion="{}"
                    data-agregados="{}"
                    data-slump="{}"
                    data-estado="{}"
                    data-nota="{}"
                    data-cantidad-yardas="{}"
                    data-precio-yarda="{}"
                    data-precio-total="{}">
                <span class="material-symbols-outlined">info</span>
            </a>
            
            ''',
            obj.id,
            obj.cliente.nombre_apellido,
            obj.cliente.tipo_documento,
            obj.cliente.numero,
            obj.fecha_entrega,
            obj.hora_entrega,
            obj.direccion_entrega,
            obj.agregados or "",
            obj.slump or "",
            obj.estado_pedido,
            obj.nota or "",
            obj.cantidad_yardas or "",
            obj.precio_yarda or "",
            obj.precio_total or ""
        )

    def estado(self, obj):
        return format_html('<span class="inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400">{}</span>', obj.estado_pedido)
    
    def despachos(self, obj):
        return format_html('<a class="btn" href="#"><span class="material-symbols-outlined text-green-700 dark:text-green-200">delivery_truck_bolt</span></a>', obj.id)
        
    list_display        = ('cliente', 'codigo_pedido', 'cantidad_yardas', 'precio_yarda', 'precio_total', 'estado', 'mas_detalles', 'despachos', 'editar','eliminar',)
    list_filter         = []
    search_fields       = ('cliente__tipo_documento','cliente__numero', 'codigo_pedido',)
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True
    readonly_fields    = ('cliente', 'codigo_pedido' , 'fecha_entrega', 'hora_entrega', 'direccion_entrega')
    
     # Configuración de los formularios de edición y creación
    fieldsets = [
        (
            ("Asignación"), 
            {
                "classes":  ["tab"],
                "fields":   ['agregados', 'slump', 'estado_pedido'],
            }
        ),
        (
            ("Precios"), 
            {
                "classes":  ["tab"],
                "fields":   ['cantidad_yardas','precio_yarda','precio_total'],
            }
        ),
    ]
    
    class Media:
        js = (
            'admin/js/pedido_modal.js',
            'admin/js/pedido_admin.js',
            'admin/js/pedido_asignacion.js')
        
        
@admin.register(Entrega)
class EntregaAdmin(ModelAdmin):
     # Cambia esto para mostrar 10 registros por página
    list_per_page = 10
    
    def editar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/entrega/{}/change/"><span class="material-symbols-outlined text-blue-700 dark:text-blue-200">edit</span></a>', obj.id)
    def eliminar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/entrega/{}/delete/"><span class="material-symbols-outlined text-red-700 dark:text-red-200">delete</span></a>', obj.id)

    list_display        = ( 'codigo_entrega', 'pedido', 'vehiculo', 'conductor', 'entregado',  'editar','eliminar')
    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True
    readonly_fields    = ('codigo_entrega','is_delete',)
    
     # Configuración de los formularios de edición y creación
    # fieldsets = [
    #     (
    #         ("Asignar pedido"), 
    #         {
    #             "classes":  ["tab"],
    #             "fields":   ['conductor','vehiculo','estado_pedido'],
    #         }
    #     ),
    #     (
    #         ("Asignar yardas y precios"), 
    #         {
    #             "classes":  ["tab"],
    #             "fields":   ['cantidad_yardas','precio_yarda','precio_total'],
    #         }
    #     ),
    # ]
    
   