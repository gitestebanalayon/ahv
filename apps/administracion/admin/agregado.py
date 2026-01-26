# apps/auxiliares/admin.py
from django.contrib import admin
from django.utils.html import format_html
from apps.administracion.models.agregado import Agregado

@admin.register(Agregado)
class AgregadoAdmin(admin.ModelAdmin):
    
    def editar(self, obj):
        return format_html('<a class="btn" href="/admin/administracion/agregado/{}/change/"><span class="material-symbols-outlined text-blue-700 dark:text-blue-200">edit</span></a>', obj.id)
    def eliminar(self, obj):
        return format_html('<a class="btn" href="/admin/administracion/agregado/{}/delete/"><span class="material-symbols-outlined text-red-700 dark:text-red-200">delete</span></a>', obj.id)

    list_display = ('nombre', 'descripcion', 'precio_actual', 'editar', 'eliminar')

    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True
    
    fieldsets = [
        (
            ("Agregado"), 
            {
                "classes":  ["tab"],
                "fields":   ['nombre', 'descripcion'],
            }
        ),

    ]
    
    
    def precio_actual(self, obj):
        precio = obj.precios.filter(is_active=True).first()
        if precio:
            return f"${precio.precio}"
        return "Sin precio"
    precio_actual.short_description = 'Precio Actual'