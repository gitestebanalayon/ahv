from django.contrib                 import admin, messages
from django.http import HttpResponseRedirect
from django.utils.translation       import ngettext, gettext_lazy as _
from django.utils.html              import format_html
from django.utils.http              import urlencode
from django.shortcuts               import render, redirect, get_object_or_404
from django.urls                    import reverse, path
from django                         import forms
from django.core.exceptions import ValidationError


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

from apps.sistema.models.pedido import Pedido, Entrega
from apps.sistema.models.conductor import Conductor
from apps.sistema.models.vehiculo import Vehiculo

class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['vehiculo', 'conductor', 'secuencia', 'yardas_asignadas', 
                 'fecha_hora_salida', 'fecha_hora_entrega', 'nota']

@admin.register(Pedido)
class PedidoAdmin(ModelAdmin):
     # Cambia esto para mostrar 10 registros por página
    list_per_page = 10
    
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
            return format_html(
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
        return format_html('<span class="font-semibold text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300">{}</span>', obj.codigo_pedido)
        
  

    list_display        = ('cliente', 'numero_orden', 'cantidad_yardas', 'slump', 'estado', 'mas_detalles', 'entregas_realizadas', 'despachos',)
    list_filter         = []
    search_fields       = ('cliente__tipo_documento','cliente__numero', 'codigo_pedido',)
    list_display_links  = None
    actions             = None #[desactivar, reactivar]
    list_select_related = True
    readonly_fields    = ('cliente', 'codigo_pedido' , 'fecha_entrega', 'hora_entrega', 'direccion_entrega')
    
     # Configuración de los formularios de edición y creación
    # fieldsets = [
    #     (
    #         ("Asignación"), 
    #         {
    #             "classes":  ["tab"],
    #             "fields":   ['agregados', 'slump', 'estado_pedido'],
    #         }
    #     ),
    #     (
    #         ("Precios"), 
    #         {
    #             "classes":  ["tab"],
    #             "fields":   ['cantidad_yardas','precio_yarda','precio_total'],
    #         }
    #     ),
    # ]
    
    # VISTA PERSONALIZADA PARA DESPACHOS
    # En tu vista (admin.py)
    # En apps/sistema/admin/pedido.py - En la clase PedidoAdmin

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
    
    class Media:
        js = (
            'admin/js/pedido_modal.js',
            'admin/js/pedido_admin.js')
        
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
        return format_html('<a class="btn" href="/admin/sistema/entrega/{}/change/"><span class="material-symbols-outlined text-blue-700 dark:text-blue-200">edit</span></a>', obj.id)
    def eliminar(self, obj):
        return format_html('<a class="btn" href="/admin/sistema/entrega/{}/delete/"><span class="material-symbols-outlined text-red-700 dark:text-red-200">delete</span></a>', obj.id)

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
   