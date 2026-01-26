# # apps/auxiliares/admin.py
# from django.contrib import admin
# from django.utils.html import format_html
# from apps.administracion.models.rango_pedido import RangoPedido
# from apps.administracion.models.precio_rango_pedido import PrecioRangoPedido
# from apps.administracion.models.agregado import Agregado
# from apps.administracion.models.agregado_precio import AgregadoPrecio

# class PrecioRangoPedidoInline(admin.TabularInline):
#     model = PrecioRangoPedido
#     extra = 1
#     fields = ('codigo', 'precio_por_yarda', 'fecha_inicio', 'fecha_fin', 'motivo_cambio', 'is_delete')
#     readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

# @admin.register(RangoPedido)
# class RangoPedidoAdmin(admin.ModelAdmin):
#     list_display = ('codigo', 'nombre', 'rango_display', 'precio_actual', 'is_delete')
#     list_filter = ('is_delete',)
#     inlines = [PrecioRangoPedidoInline]
#     search_fields = ('nombre', 'descripcion')
    
#     def rango_display(self, obj):
#         if obj.yarda_maxima:
#             return f"{obj.yarda_minima} - {obj.yarda_maxima} yd"
#         return f"{obj.yarda_minima}+ yd"
#     rango_display.short_description = 'Rango'
    
#     def precio_actual(self, obj):
#         precio = obj.precios.filter(fecha_fin__isnull=True, is_delete=False).first()
#         if precio:
#             return f"${precio.precio_por_yarda}/yd"
#         return "Sin precio"
#     precio_actual.short_description = 'Precio Actual'

# class AgregadoPrecioInline(admin.TabularInline):
#     model = AgregadoPrecio
#     extra = 1
#     fields = ('precio', 'fecha_inicio', 'fecha_fin', 'motivo_cambio', 'is_active')
#     readonly_fields = ('fecha_creacion', 'fecha_actualizacion')

# @admin.register(Agregado)
# class AgregadoAdmin(admin.ModelAdmin):
    
#     def editar(self, obj):
#         return format_html('<a class="btn" href="/admin/administracion/agregado/{}/change/"><span class="material-symbols-outlined text-blue-700 dark:text-blue-200">edit</span></a>', obj.id)
#     def eliminar(self, obj):
#         return format_html('<a class="btn" href="/admin/administracion/agregado/{}/delete/"><span class="material-symbols-outlined text-red-700 dark:text-red-200">delete</span></a>', obj.id)

#     list_display = ('nombre', 'descripcion', 'precio_actual', 'is_delete', 'editar', 'eliminar')

#     inlines = [AgregadoPrecioInline]
#     list_filter         = []
#     search_fields       = []
#     list_display_links  = None
#     actions             = None #[desactivar, reactivar]
#     list_select_related = True
    
#     def precio_actual(self, obj):
#         precio = obj.precios.filter(is_active=True).first()
#         if precio:
#             return f"${precio.precio}"
#         return "Sin precio"
#     precio_actual.short_description = 'Precio Actual'