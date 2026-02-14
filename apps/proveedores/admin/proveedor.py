# apps/auxiliares/admin.py
from django.contrib import admin
from django.utils.html import format_html
from apps.proveedores.models.proveedor import Proveedor

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    
    def editar(self, obj):
        return format_html('<a class="btn" href="/admin/proveedores/proveedor/{}/change/"><span class="material-symbols-outlined text-primary-600 dark:text-primary-600">edit</span></a>', obj.id)
    def eliminar(self, obj):
        return format_html('<a class="btn" href="/admin/proveedores/proveedor/{}/delete/"><span class="material-symbols-outlined text-red-600 dark:text-red-600">delete</span></a>', obj.id)

    list_display = ('nombre_comercial', 'editar', 'eliminar')

    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True
    
    fieldsets = [
        (
            ("Proveedor"), 
            {
                "classes":  ["tab"],
                "fields":   ['nombre_comercial'],
            }
        ),

    ]