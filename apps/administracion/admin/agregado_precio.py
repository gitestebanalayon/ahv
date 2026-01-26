from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from django.urls import reverse
from django.shortcuts import get_object_or_404

from unfold.admin import ModelAdmin
from unfold.contrib.filters.admin import RelatedDropdownFilter

from apps.administracion.models.agregado_precio import AgregadoPrecio

@admin.register(AgregadoPrecio)
class AgregadoPrecioAdmin(ModelAdmin):
    list_per_page = 10
    show_full_result_count = False
    list_filter_submit = True

    def editar(self, obj):
        """Mostrar botón de editar solo si is_active=True"""
        if obj.is_active:
            return format_html(
                '<a class="btn" href="{}">'
                '<span class="material-symbols-outlined text-blue-700 dark:text-blue-200">edit</span>'
                '</a>', 
                reverse('admin:administracion_agregadoprecio_change', args=[obj.id])
            )
        else:
            return format_html(
                '<span class="text-gray-400 dark:text-gray-500 cursor-not-allowed">'
                '<span class="material-symbols-outlined">lock</span>'
                '</span>'
            )
    
    def eliminar(self, obj):
        """Mostrar botón de eliminar siempre"""
        return format_html(
            '<a class="btn" href="{}">'
            '<span class="material-symbols-outlined text-red-700 dark:text-red-200">delete</span>'
            '</a>', 
            reverse('admin:administracion_agregadoprecio_delete', args=[obj.id])
        )
    
    def get_agregado_nombre(self, obj):
        """Mostrar nombre del agregado"""
        return obj.agregado.nombre if obj.agregado else "-"
    get_agregado_nombre.short_description = 'Agregado'
    get_agregado_nombre.admin_order_field = 'agregado__nombre'
  
    list_display = (
        'get_agregado_nombre',
        'precio',
        'fecha_inicio',
        'fecha_fin',
        'is_active',
        'editar',
        'eliminar'
    )
    
    list_filter = [
        ('agregado', RelatedDropdownFilter),
    ]
    
    list_display_links = None
    actions = None
    list_select_related = ['agregado']
    ordering = ['-fecha_inicio']
    
    fieldsets = [
        (
            ("Precios de Agregados"), 
            {
                "classes":  ["tab"],
                "fields":   ['agregado', 'precio', 'motivo_cambio'],
            }
        ),
    ]
    
    def get_readonly_fields(self, request, obj=None):
        """Hacer campos de solo lectura si el registro está inactivo"""
        readonly_fields = []
        
        # Si el objeto existe y está inactivo, hacer todos los campos de solo lectura
        if obj and not obj.is_active:
            # Obtener todos los campos del modelo excepto algunos específicos
            all_fields = [field.name for field in self.model._meta.fields]
            # Excluir campos que no quieres que sean de solo lectura
            excluded_fields = ['is_active']  # Mantener editable si quieres
            readonly_fields = [f for f in all_fields if f not in excluded_fields]
        
        return readonly_fields
    
    def has_change_permission(self, request, obj=None):
        """Verificar si el usuario puede editar el objeto"""
        if obj and not obj.is_active:
            # No permitir editar si el objeto está inactivo
            return False
        return super().has_change_permission(request, obj)
    
    def get_queryset(self, request):
        """Retornar queryset vacío inicialmente solo en la vista de lista"""
        qs = super().get_queryset(request)
        
        # Verificar si estamos en la vista de lista (changelist)
        if not self.is_changelist_request(request):
            return qs
        
        # Solo para la vista de lista, verificar si hay filtros
        if not self.has_search_or_filters(request):
            return qs.none()
        
        return qs
    
    def is_changelist_request(self, request):
        """Verificar si es una solicitud de la vista de lista (changelist)"""
        path_info = request.path_info
        
        # Si la ruta contiene change, delete, history, etc., no es changelist
        non_changelist_patterns = ['/change/', '/delete/', '/history/', '/add/']
        
        for pattern in non_changelist_patterns:
            if pattern in path_info:
                return False
        
        # Verificar si es la URL base del modelo
        changelist_patterns = ['/admin/administracion/agregadoprecio/', '/admin/administracion/agregadoprecio']
        
        for pattern in changelist_patterns:
            if path_info.startswith(pattern):
                remaining = path_info[len(pattern):]
                if not remaining or remaining == '/' or '?' in remaining:
                    return True
        
        return False
    
    def has_search_or_filters(self, request):
        """Verificar si hay búsqueda o filtros aplicados en la vista de lista"""
        if not self.is_changelist_request(request):
            return True
        
        # Verificar búsqueda por texto
        if 'q' in request.GET and request.GET['q'].strip():
            return True
        
        # Verificar todos los parámetros que podrían ser filtros
        for key, value in request.GET.items():
            if key in ['p', 'o', 'ot']:
                continue
            if value:
                return True
        
        return False
    
    def get_search_results(self, request, queryset, search_term):
        """Personalizar los resultados de búsqueda"""
        if self.is_changelist_request(request) and not self.has_search_or_filters(request):
            return queryset.none(), False
        
        return super().get_search_results(request, queryset, search_term)
    
    def change_view(self, request, object_id, form_url='', extra_context=None):
        """Personalizar la vista de edición"""
        # Obtener el objeto
        obj = self.get_object(request, object_id)
        
        # Verificar si el objeto está activo
        if obj and not obj.is_active:
            # Agregar mensaje de advertencia
            if extra_context is None:
                extra_context = {}
            extra_context['warning_message'] = _(
                "Este registro está inactivo. No se puede editar."
            )
        
        return super().change_view(request, object_id, form_url, extra_context)