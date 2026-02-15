from django.contrib                 import admin, messages
from django.http import HttpResponseRedirect
from django.utils.translation       import ngettext, gettext_lazy as _
from django.utils.html              import format_html
from django.utils.http              import urlencode
from django.shortcuts               import render, redirect, get_object_or_404
from django.urls                    import reverse, path
from django                         import forms
from django.core.exceptions import ValidationError
from django.db.models import Sum
from django.utils.safestring import mark_safe

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

from apps.cuenta.models import User
from apps.sistema.models.pedido import Pedido, Entrega
from apps.administracion.models.agregado import Agregado
from apps.sistema.models.conductor import Conductor
from apps.sistema.models.vehiculo import Vehiculo
from apps.sistema.models.pedido_agregado import PedidoAgregado

# class EntregaForm(forms.ModelForm):
#     class Meta:
#         model = Entrega
#         fields = ['vehiculo', 'conductor', 'secuencia', 'yardas_asignadas', 
#                  'fecha_hora_salida', 'fecha_hora_entrega', 'nota']

class PedidoAgregadoInline(admin.TabularInline):
    model = PedidoAgregado
    extra = 0
    verbose_name = "Precio de Agregado"
    verbose_name_plural = "Precios de Agregados (Detalle)"
    fields = ['agregado', 'precio_aplicado', 'precio_aplicado_codigo']
    readonly_fields = ['precio_aplicado', 'precio_aplicado_codigo']
    classes = ['collapse']  # Opcional: colapsado por defecto


class PedidoAdminForm(forms.ModelForm):
    """
    Formulario con las FLECHITAS que quieres
    """
    # Variable para controlar si ya sincronizamos
    _sincronizado = False
    
    class Meta:
        model = Pedido
        fields = '__all__'
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar queryset
        self.fields['agregado'].queryset = Agregado.objects.filter(
            is_delete=False
        ).order_by('nombre')
    
    def save(self, commit=True):
        """
        Guarda el pedido y SINCRONIZA los precios en PedidoAgregado
        Maneja correctamente commit=False y commit=True
        """
     
        # Guardar el objeto (puede ser con commit True o False)
        pedido = super().save(commit=commit)
        
        if commit:
            self.save_m2m()
            # Sincronizar precios SOLO si no se ha sincronizado ya
            if not self._sincronizado:
                self.sincronizar_precios_agregados(pedido)
                self._sincronizado = True
            else:
                print("Ya sincronizado anteriormente, omitiendo...")
            
        else: 
            # Guardar los datos para cuando se haga commit=True
            self.pedido_temporal = pedido
            self.agregados_seleccionados = self.cleaned_data.get('agregado', [])
        
        return pedido
    
    def sincronizar_precios_agregados(self, pedido):
        """
        Toma los agregados seleccionados y crea/actualiza PedidoAgregado
        """
        from apps.administracion.models.agregado_precio import AgregadoPrecio
        
      
        
        # Obtener IDs de agregados seleccionados
        # Usar los guardados o los del cleaned_data
        if hasattr(self, 'agregados_seleccionados'):
            agregados_seleccionados = self.agregados_seleccionados
           
        else:
            agregados_seleccionados = self.cleaned_data.get('agregado', [])
        
        
     
        if not agregados_seleccionados:
            PedidoAgregado.objects.filter(pedido=pedido).delete()
            self.recalcular_subtotales(pedido)
            return
        
        # Eliminar precios de agregados que ya no están
        eliminados = PedidoAgregado.objects.filter(pedido=pedido).exclude(
            agregado__in=agregados_seleccionados
        ).delete()
       
        
        # Crear o actualizar precios para los agregados seleccionados
        creados = 0
        actualizados = 0
        
        for agregado in agregados_seleccionados:
            # Buscar precio actual del agregado
            precio_actual = AgregadoPrecio.objects.filter(
                agregado=agregado,
                is_active=True
            ).order_by('-fecha_inicio').first()
            
            if precio_actual:
                precio = precio_actual.precio
                codigo = precio_actual.codigo
                
            else:
                precio = 0
                codigo = None
               
            
            # Crear o actualizar
            obj, created = PedidoAgregado.objects.update_or_create(
                pedido=pedido,
                agregado=agregado,
                defaults={
                    'precio_aplicado': precio,
                    'precio_aplicado_codigo': codigo
                }
            )
            
            if created:
                creados += 1
            else:
                actualizados += 1
        
     
        # Verificar que se guardaron
        # total = PedidoAgregado.objects.filter(pedido=pedido).count()
        
        
        # Recalcular subtotales
        self.recalcular_subtotales(pedido)
       
    
    def recalcular_subtotales(self, pedido):
        """Recalcula subtotales basado en PedidoAgregado"""
        total_agregados = PedidoAgregado.objects.filter(pedido=pedido).aggregate(
            total=Sum('precio_aplicado')
        )['total'] or 0
        
        pedido.subtotal_agregados = total_agregados
        pedido.precio_total = (pedido.subtotal_yardas or 0) + total_agregados + (pedido.subtotal_hultdelivery or 0)
        pedido.save(update_fields=['subtotal_agregados', 'precio_total'])
     
        
@admin.register(Pedido)
class PedidoAdmin(ModelAdmin):
    form = PedidoAdminForm
    
    filter_horizontal = ['agregado']
    
     # Cambia esto para mostrar 10 registros por página
    list_per_page = 10
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtrar campo ForeignKey cliente"""
        if db_field.name == "cliente":
            # Filtrar solo usuarios clientes activos
            kwargs["queryset"] = User.objects.filter(is_customer=True, is_active=True).order_by('username')
        
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
    
    # Sobrescribir get_urls para agregar nuestra vista personalizada
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'entrega/<int:pedido_id>/',
                self.admin_site.admin_view(self.entrega_view),
                name='pedido-entrega'
            ),
        ]
        return custom_urls + urls
  

    # def editar(self, obj):
    #     return format_html('<a class="btn" href="/admin/sistema/pedido/{}/change/"><span class="material-symbols-outlined text-primary-700 dark:text-primary-200">edit</span></a>', obj.id)
    # def eliminar(self, obj):
    #     return format_html('<a class="btn" href="/admin/sistema/pedido/{}/delete/"><span class="material-symbols-outlined text-red-700 dark:text-red-200">delete</span></a>', obj.id)

    def mas_detalles(self, obj):
        # Crear lista de agregados como badges HTML
        agregados_badges = ""
        for agregado in obj.agregado.all():
            agregados_badges += f'''
            <span class="inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap bg-primary-100 text-primary-700 dark:bg-primary-500/20 dark:text-base-100">
                {agregado.nombre}
            </span>
            '''
        
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
                    data-agregados='{}'
                    data-agregados-badges='{}'
                    data-slump="{}"
                    data-estado="{}"
                    data-nota="{}"
                    data-cantidad-yardas="{}"
                
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
            ", ".join([a.nombre for a in obj.agregado.all()]),  # Texto simple
            agregados_badges,  # HTML de badges
            obj.slump or "",
            obj.estado_pedido,
            obj.nota or "",
            obj.cantidad_yardas or "",
            # obj.precio_yarda or "",
            obj.precio_total or ""
        )

    def estado(self, obj):
        # Definir colores y clases para cada estado
        estados_colores = {
            'pendiente': {
                'clase': 'badge-warning',
                'icono': 'schedule',  # Reloj
            },
            'programado': {
                'clase': 'badge-info',
                'icono': 'calendar_month'  # Calendario
            },
            'en viaje': {
                'clase': 'badge-primary',
                'icono': 'delivery_truck_speed'  # Camión
            },
            'completado': {
                'clase': 'badge-success',
                'icono': 'done_all'  # Check
            },
            'cancelado': {
                'clase': 'badge-danger',
                'icono': 'cancel'  # Cancel
            }
        }
        
        # Obtener el estado en minúsculas para comparación
        estado_actual = str(obj.estado_pedido).lower().strip()
        
        # Obtener configuración del estado o usar valores por defecto
        config = estados_colores.get(estado_actual, {
            'clase': 'badge-secondary',
            'icono': '❓'
        })
        
        # Formatear el HTML con el estado
        return format_html(
            '<span class="inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold {}">'
                '<span class="material-symbols-outlined text-sm">'
                    '{}'
                '</span>'
                    '{}'
            '</span>',
            config['clase'],
            config['icono'],
            obj.estado_pedido
        )
    
    def despachos(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/pedido/entrega/{}/"><span class="material-symbols-outlined text-green-700 dark:text-green-200">delivery_truck_bolt</span></a>', obj.id)
        
    def entregas_realizadas(self, obj):
        # Mostrar el número de entregas realizadas para este pedido
        count = obj.entrega_set.count()

        if count == 0:
            return mark_safe(
            '<a class="inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap bg-base-100 text-base-700 dark:bg-base-500/20 dark:text-base-200" '
            'title="Ver entregas">'
            'Sin entregas'
            '</a>',
        )

        if count == 1:
            return format_html(
            '<a class="inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400" '
            'title="Ver entregas">'
            '{} entrega'
            '</a>',
            count
        )

        return format_html(
            '<a class="inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap bg-green-100 text-green-700 dark:bg-green-500/20 dark:text-green-400" '
            'title="Ver entregas">'
            '{} entregas'
            '</a>',
            count
        )
    entregas_realizadas.short_description = "Entregas"    
        
    def numero_orden(self, obj):
        return format_html('<span class="font-semibold text-primary-600 hover:text-primary-800 dark:text-primary-400 dark:hover:text-primary-300">{}</span>', obj.codigo_pedido)
        
    def editar(self, obj):
        # Verificar si el usuario tiene permiso de cambio (change) Y si no está completado
        if self.has_change_permission(self.request, obj=obj) and str(obj.estado_pedido).lower() != 'completado':
            return format_html(
                '<a class="btn" href="/admin/sistema/pedido/{}/change/" title="Editar pedido">'
                '<span class="material-symbols-outlined text-primary-600 dark:text-primary-200">edit</span>'
                '</a>', 
                obj.id
            )
        # Si está completado, mostrar icono bloqueado
        elif str(obj.estado_pedido).lower() == 'completado':
            # Opción 1: Usar mark_safe (recomendado)
            from django.utils.safestring import mark_safe
            return mark_safe(
                '<span class="btn" title="Pedido completado - No editable">'
                '<span class="material-symbols-outlined text-gray-400 dark:text-gray-600">lock</span>'
                '</span>'
            )
        return ""

    editar.short_description = ''  # Esto oculta el encabezado de la columna
    editar.allow_tags = True  # Permite renderizar HTML en la columna

    def eliminar(self, obj):
        # Verificar si el usuario tiene permiso de eliminación (delete) Y si no está completado
        if self.has_delete_permission(self.request, obj=obj) and str(obj.estado_pedido).lower() != 'completado':
            return format_html(
                '<a class="btn" href="/admin/sistema/pedido/{}/delete/" title="Eliminar pedido">'
                '<span class="material-symbols-outlined text-red-600 dark:text-red-200">delete</span>'
                '</a>', 
                obj.id
            )
        # Si está completado, mostrar icono bloqueado
        elif str(obj.estado_pedido).lower() == 'completado':
            from django.utils.safestring import mark_safe
            return mark_safe(
                '<span class="btn" title="Pedido completado - No eliminable">'
                '<span class="material-symbols-outlined text-gray-400 dark:text-gray-600">lock</span>'
                '</span>'
            )
        return ""

    eliminar.short_description = ''  # Esto oculta el encabezado de la columna
    eliminar.allow_tags = True
    
    def has_change_permission(self, request, obj=None):
        """
        Sobrescribir para no permitir editar pedidos completados o cancelados
        """
        if obj is not None:
            estado_actual = str(obj.estado_pedido).lower().strip()
            if estado_actual in ['completado', 'cancelado']:
                return False
        
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        Sobrescribir para no permitir eliminar pedidos en ciertos estados
        """
        if obj is not None:
            estado_actual = str(obj.estado_pedido).lower().strip()
            if estado_actual in ['completado', 'cancelado', 'en viaje', 'programado']:
                return False
        
        return super().has_delete_permission(request, obj)

    def get_queryset(self, request):
        # Guardar request para usarlo en los métodos
        self.request = request
        return super().get_queryset(request)

    # AÑADE ESTE MÉTODO PARA MOSTRAR LOS AGREGADOS
    def mostrar_agregados(self, obj):
        """Método personalizado para mostrar agregados en list_display"""
        agregados = obj.agregado.all()
        if agregados:
            # Mostrar como lista compacta
            nombres = [agregado.nombre for agregado in agregados[:3]]
            display = ", ".join(nombres)
            if agregados.count() > 3:
                display += f" (+{agregados.count() - 3})"
            return display
        return "-"
    
    mostrar_agregados.short_description = "Agregados"

    list_display        = ('cliente', 'numero_orden', 'tipo_concreto', 'cantidad_yardas', 'slump', 'estado', 'mas_detalles', 'entregas_realizadas', 'despachos', 'editar', 'eliminar')
    list_filter         = ()
    search_fields       = ('cliente__tipo_documento','cliente__numero', 'codigo_pedido',)
    # list_display_links  = None
    # actions             = None #[desactivar, reactivar]
    # list_select_related = True
    readonly_fields    = ('codigo_pedido',)
    
    
    
    fieldsets = [
        (
            ("Pedido"), 
            {
                "classes": ["tab"],
                "fields": [
                    'cliente', 
                    'tipo_concreto', 
                    'cantidad_yardas', 
                    'slump', 
                    'agregado',  # 👈 ESTE CAMPO TENDRÁ LAS FLECHITAS
                    'fecha_entrega', 
                    'hora_entrega', 
                    'direccion_entrega', 
                    'nota'
                ],
            }
        ),
    ]
    
    def entrega_view(self, request, pedido_id):
        pedido = get_object_or_404(Pedido, id=pedido_id)
        
        # Obtener todas las entregas existentes para este pedido
        entregas_existentes = Entrega.objects.filter(pedido=pedido).order_by('secuencia')
        
        # Calcular totales - EXCLUIR ENTREGAS CANCELADAS
        # Sumar solo las yardas de entregas NO canceladas
        entregas_activas = entregas_existentes.exclude(estado='cancelado')
        total_yardas_asignadas = sum([float(e.yardas_asignadas) for e in entregas_activas])
        
        # También excluir canceladas para las entregas completadas
        entregas_completadas = entregas_activas.filter(entregado=True).count()
        
        # Calcular yardas pendientes
        yardas_pendientes = float(pedido.cantidad_yardas) - total_yardas_asignadas if pedido.cantidad_yardas else 0
        
        context = {
            **self.admin_site.each_context(request),
            'codigo_pedido': f'{pedido.codigo_pedido}',
            'pedido': pedido,
            'entregas_existentes': entregas_existentes,
            'total_yardas_asignadas': total_yardas_asignadas,
            'yardas_pendientes': yardas_pendientes,
            'total_entregas': entregas_existentes.count(),
            'entregas_completadas': entregas_completadas,
            'entregas_canceladas': entregas_existentes.filter(estado='cancelado').count(),
            'opts': self.model._meta,
            'app_label': self.model._meta.app_label,
            'has_change_permission': self.has_change_permission(request),
        }
        
        return render(request, 'admin/sistema/pedido/entrega.html', context)
    
    def save_form(self, request, form, change):
        """
        Sobrescribir save_form para manejar correctamente los ManyToManyField
        """
        # Primero guardamos el formulario normalmente
        obj = super().save_form(request, form, change)
        
        # Si es un nuevo pedido, calcular código
        # if not obj.codigo_pedido:
        #     obj.codigo_pedido = obj.generar_codigo_pedido()
        
        return obj
    
    def save_model(self, request, obj, form, change):
        """
        Guarda el modelo
        """
       
        super().save_model(request, obj, form, change)
       
    def save_related(self, request, form, formsets, change):
        """
        Guarda las relaciones
        """
       
        super().save_related(request, form, formsets, change)
        
        # Si por alguna razón no se sincronizó en save(), hacerlo aquí
        obj = form.instance
        if not hasattr(form, '_sincronizado') or not form._sincronizado:
         
            form.sincronizar_precios_agregados(obj)
            form._sincronizado = True
        
       
    

    def response_add(self, request, obj, post_url_continue=None):
        """
        Redirigir después de agregar
        """
        # Recalcular por si acaso
        obj.calcular_precios()
        obj.save()
        
        return super().response_add(request, obj, post_url_continue)
    
    def response_change(self, request, obj):
        """
        Redirigir después de editar
        """
        # Recalcular por si acaso
        obj.calcular_precios()
        obj.save()
        
        return super().response_change(request, obj)   
     

    class Media:
        # css = {
        #     'all': ('admin/css/widgets.css',)  # CSS necesario para filter_horizontal
        # }
        js = (
            'admin/js/pedido_modal.js',
            'admin/js/pedido_admin.js',
            'admin/js/SelectBox.js',
            'admin/js/SelectFilter2.js')
        
@admin.register(Entrega)
class EntregaAdmin(ModelAdmin):
      # Ocultar completamente del índice del admin
    def has_module_permission(self, request):
        return False
    
    # Pero permitir acceso desde otras vistas
    def has_view_permission(self, request, obj=None):
        return True
    
     # Cambia esto para mostrar 10 registros por página
    list_per_page = 10
    
    def editar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/entrega/{}/change/"><span class="material-symbols-outlined text-primary-600 dark:text-primary-200">edit</span></a>', obj.id)
    def eliminar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/entrega/{}/delete/"><span class="material-symbols-outlined text-red-600 dark:text-red-200">delete</span></a>', obj.id)

    def acciones(self, obj):
        html = ''
        if obj.estado == 'programado':
            html += f'''
                <a href="{reverse('admin:marcar_iniciado', args=[obj.id])}" 
                   class="button" 
                   style="background-color: #4CAF50; color: white; padding: 5px 10px; border-radius: 5px; margin-right: 5px;">
                    Iniciar Entrega
                </a>
            '''
        if obj.estado in ['programado', 'en_camino']:
            html += f'''
                <a href="{reverse('admin:marcar_completado', args=[obj.id])}" 
                   class="button" 
                   style="background-color: #2196F3; color: white; padding: 5px 10px; border-radius: 5px; margin-right: 5px;">
                    Completar
                </a>
                <a href="{reverse('admin:cancelar_entrega', args=[obj.id])}" 
                   class="button" 
                   style="background-color: #f44336; color: white; padding: 5px 10px; border-radius: 5px;">
                    Cancelar
                </a>
            '''
        return format_html(html)
    acciones.short_description = 'Acciones'

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom_urls = [
            path('<int:entrega_id>/iniciar/', 
                 self.admin_site.admin_view(self.marcar_iniciado_view), 
                 name='marcar_iniciado'),
            path('<int:entrega_id>/completar/', 
                 self.admin_site.admin_view(self.marcar_completado_view), 
                 name='marcar_completado'),
            path('<int:entrega_id>/cancelar/', 
                 self.admin_site.admin_view(self.cancelar_view), 
                 name='cancelar_entrega'),
            path('<int:entrega_id>/restablecer/',  # NUEVA RUTA
                self.admin_site.admin_view(self.restablecer_view), 
                name='restablecer_entrega'),
        ]
        return custom_urls + urls

   

    def marcar_iniciado_view(self, request, entrega_id):
        """Vista para iniciar una entrega"""
        try:
            # Obtener la entrega
            entrega = Entrega.objects.get(id=entrega_id)
            
            # Intentar iniciar la entrega
            entrega.marcar_como_iniciado()
            
            # Éxito
            messages.success(request, f'✅ Entrega {entrega.codigo_entrega} iniciada exitosamente.')
            
        except ValidationError as e:
            # Capturar errores de validación y mostrarlos como mensajes
            error_message = str(e)
            
            # Si es una lista, tomar el primer mensaje
            if hasattr(e, 'messages') and e.messages:
                if isinstance(e.messages, list):
                    error_message = e.messages[0]
                else:
                    error_message = str(e.messages)
            
            # Mostrar mensaje de error
            messages.error(request, f'❌ {error_message}')
            
        except Entrega.DoesNotExist:
            messages.error(request, '❌ Entrega no encontrada.')
            
        except Exception as e:
            # Error inesperado
            messages.error(request, f'❌ Error inesperado: {str(e)}')
        
        # Redirigir siempre
        try:
            if 'entrega' in locals() and hasattr(entrega, 'pedido') and entrega.pedido:
                return HttpResponseRedirect(
                    reverse('admin:pedido-entrega', args=[entrega.pedido.id])
                )
            else:
                # Intentar obtener pedido_id de los parámetros GET
                pedido_id = request.GET.get('pedido_id')
                if pedido_id:
                    return HttpResponseRedirect(
                        reverse('admin:pedido-entrega', args=[pedido_id])
                    )
                else:
                    return HttpResponseRedirect(reverse('admin:sistema_entrega_changelist'))
                    
        except Exception:
            # Si hay error en la redirección, ir a la lista de entregas
            return HttpResponseRedirect(reverse('admin:sistema_entrega_changelist'))
        
    def marcar_completado_view(self, request, entrega_id):
        try:
            entrega = Entrega.objects.get(id=entrega_id)
            entrega.marcar_como_completado()
            messages.success(request, f'Entrega {entrega.codigo_entrega} completada exitosamente')
            
            # Redirigir a la vista de entregas del pedido
            return HttpResponseRedirect(
                reverse('admin:pedido-entrega', args=[entrega.pedido.id])
            )
            
        except Entrega.DoesNotExist:
            messages.error(request, 'Entrega no encontrada')
            return HttpResponseRedirect(reverse('admin:sistema_entrega_changelist'))
        except ValidationError as e:
            messages.error(request, str(e))
            # Intentar obtener el pedido para redirigir
            try:
                entrega = Entrega.objects.get(id=entrega_id)
                return HttpResponseRedirect(
                    reverse('admin:pedido-entrega', args=[entrega.pedido.id])
                )
            except:
                return HttpResponseRedirect(reverse('admin:sistema_entrega_changelist'))
        
    def cancelar_view(self, request, entrega_id):
        try:
            entrega = Entrega.objects.get(id=entrega_id)
            entrega.cancelar()
            messages.success(request, f'Entrega {entrega.codigo_entrega} cancelada')
            
            # Redirigir a la vista de entregas del pedido
            return HttpResponseRedirect(
                reverse('admin:pedido-entrega', args=[entrega.pedido.id])
            )
            
        except Entrega.DoesNotExist:
            messages.error(request, 'Entrega no encontrada')
            return HttpResponseRedirect(reverse('admin:sistema_entrega_changelist'))
        except ValidationError as e:
            messages.error(request, str(e))
            # Intentar obtener el pedido para redirigir
            try:
                entrega = Entrega.objects.get(id=entrega_id)
                return HttpResponseRedirect(
                    reverse('admin:pedido-entrega', args=[entrega.pedido.id])
                )
            except:
                return HttpResponseRedirect(reverse('admin:sistema_entrega_changelist'))

    def restablecer_view(self, request, entrega_id):
        """Vista para restablecer una entrega cancelada"""
        try:
            entrega = Entrega.objects.get(id=entrega_id)
            entrega.restablecer()
            messages.success(request, f'Entrega {entrega.codigo_entrega} restablecida exitosamente')
            
            # Redirigir a la vista de entregas del pedido
            pedido_id = request.GET.get('pedido_id') or (hasattr(entrega, 'pedido') and entrega.pedido.id)
            
            if pedido_id:
                return HttpResponseRedirect(
                    reverse('admin:pedido-entrega', args=[pedido_id])
                )
            else:
                return HttpResponseRedirect(reverse('admin:sistema_entrega_changelist'))
                
        except Entrega.DoesNotExist:
            messages.error(request, 'Entrega no encontrada')
            pedido_id = request.GET.get('pedido_id')
            if pedido_id:
                return HttpResponseRedirect(
                    reverse('admin:pedido-entrega', args=[pedido_id])
                )
            return HttpResponseRedirect(reverse('admin:sistema_entrega_changelist'))
        except ValidationError as e:
            messages.error(request, str(e))
            pedido_id = request.GET.get('pedido_id')
            if pedido_id:
                return HttpResponseRedirect(
                    reverse('admin:pedido-entrega', args=[pedido_id])
                )
            return HttpResponseRedirect(reverse('admin:sistema_entrega_changelist'))
        except Exception as e:
            messages.error(request, f'Error: {str(e)}')
            pedido_id = request.GET.get('pedido_id')
            if pedido_id:
                return HttpResponseRedirect(
                    reverse('admin:pedido-entrega', args=[pedido_id])
                )
            return HttpResponseRedirect(reverse('admin:sistema_entrega_changelist'))


    exclude = ('pedido', 'secuencia')
 
    def save_model(self, request, obj, form, change):
        # Si es una creación nueva y viene de un pedido específico
        if not change and 'pedido' in request.GET:
            pedido_id = request.GET.get('pedido')
            try:
                from apps.sistema.models.pedido import Pedido
                pedido = Pedido.objects.get(id=pedido_id)
                obj.pedido = pedido
            except Pedido.DoesNotExist:
                pass
        
        super().save_model(request, obj, form, change)



    # Redirigir después de agregar
    def response_add(self, request, obj, post_url_continue=None):
        # Si el usuario hizo clic en "Guardar y continuar editando"
        if "_continue" in request.POST:
            # Mantener el comportamiento por defecto
            return super().response_add(request, obj, post_url_continue)
        
        # Si el usuario hizo clic en "Guardar y añadir otro"
        elif "_addanother" in request.POST:
            # Mantener el comportamiento por defecto pero mantener el parámetro pedido
            from django.contrib import messages
            messages.success(request, f"Entrega {obj.codigo_entrega} creada exitosamente.")
            return HttpResponseRedirect(
                f"{reverse('admin:sistema_entrega_add')}?pedido={obj.pedido.id}"
            )
        
        # Si el usuario hizo clic en "Guardar" (sin continuar)
        else:
            # Redirigir a la vista de entregas del pedido
            if hasattr(obj, 'pedido') and obj.pedido:
                return HttpResponseRedirect(
                    reverse('admin:pedido-entrega', args=[obj.pedido.id])
                )
            else:
                # Si por alguna razón no hay pedido, redirigir a la lista de entregas
                return super().response_add(request, obj, post_url_continue)
    
    # También sobrescribir response_change para la edición
    def response_change(self, request, obj):
        # Si el usuario hizo clic en "Guardar y continuar editando"
        if "_continue" in request.POST:
            return super().response_change(request, obj)
        
        # Si el usuario hizo clic en "Guardar"
        else:
            # Redirigir a la vista de entregas del pedido
            if hasattr(obj, 'pedido') and obj.pedido:
                return HttpResponseRedirect(
                    reverse('admin:pedido-entrega', args=[obj.pedido.id])
                )
            else:
                return super().response_change(request, obj)

     # También sobrescribir response_delete para la eliminación
    
    def response_delete(self, request, obj_display, obj_id):
        """
        Determina la redirección después de eliminar una entrega.
        Si venimos de un pedido específico, redirigir a la vista de entregas del pedido.
        """
        # Verificar si hay un pedido_id en los parámetros GET
        pedido_id = request.GET.get('pedido_id')
        
        if pedido_id:
            # Mostrar mensaje de éxito
            messages.success(request, f"La entrega ha sido eliminada exitosamente.")
            # Redirigir a la vista de entregas del pedido
            return HttpResponseRedirect(
                reverse('admin:pedido-entrega', args=[pedido_id])
            )
        
        # Si no hay pedido_id, usar el comportamiento por defecto
        return super().response_delete(request, obj_display, obj_id)

    list_display = ('codigo_entrega', 'pedido', 'conductor', 'vehiculo', 'acciones', 'editar', 'eliminar')
    list_filter         = []
    search_fields       = []
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True
    readonly_fields     = ('codigo_entrega','is_delete')
    
    fieldsets = [
        (
            ("Asignación de entrega"), 
            {
                "classes":  ["tab"],
                "fields":   ['conductor', 'vehiculo', 'yardas_asignadas'],
            }
        ),
        (
            ("Nota"), 
            {
                "classes":  ["tab"],
                "fields":   ['nota'],
            }
        ),
    ]
    
    class Media:
        js = (
            'admin/js/entrega_form_add.js',)
   