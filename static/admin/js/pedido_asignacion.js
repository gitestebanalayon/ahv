// static/admin/js/pedido_asignacion_robust.js

class PedidoAsignacion {
    constructor() {
        this.conductorSelect = null;
        this.vehiculoSelect = null;
        this.estadoSelect = null;
        this.vehiculoOriginal = '';
        this.apiBaseUrl = 'http://127.0.0.1:8000/';
        
        this.init();
    }
    
    init() {
        console.log('Inicializando sistema de asignación de pedidos');
        
        // Esperar un momento para asegurar que el DOM esté completamente cargado
        setTimeout(() => {
            this.encontrarCampos();
            
            if (!this.conductorSelect) {
                console.warn('No se encontró el campo conductor. El script no se ejecutará.');
                return;
            }
            
            this.configurarEventos();
            this.procesarValoresIniciales();
        }, 300);
    }
    
    encontrarCampos() {
        // Método 1: Buscar por IDs específicos de Django
        this.conductorSelect = this.buscarCampo(['id_conductor', 'conductor']);
        this.vehiculoSelect = this.buscarCampo(['id_vehiculo', 'vehiculo']);
        this.estadoSelect = this.buscarCampo(['id_estado_pedido_nombre', 'estado', 'estado_pedido']);
        
        // Hacer que el select de vehículo sea de solo lectura/visual
        this.hacerVehiculoSoloLectura();
        
        // Si no encuentra vehículo, crear uno dinámico
        if (!this.vehiculoSelect && this.conductorSelect) {
            this.crearCampoVehiculo();
            // Aplicar estilos de solo lectura al campo creado
            this.hacerVehiculoSoloLectura();
        }
    }
    
    hacerVehiculoSoloLectura() {
        if (this.vehiculoSelect) {
            // Deshabilitar el campo select
            this.vehiculoSelect.disabled = true;
            
            // Aplicar estilos visuales para indicar que es solo lectura
            this.vehiculoSelect.style.backgroundColor = '#f8f9fa';
            this.vehiculoSelect.style.color = '#495057';
            this.vehiculoSelect.style.cursor = 'not-allowed';
            this.vehiculoSelect.style.borderColor = '#ced4da';
            this.vehiculoSelect.style.opacity = '0.8';
            
            // Añadir una etiqueta o tooltip para indicar que es automático
            this.agregarTooltipVehiculo();
        }
    }
    
    agregarTooltipVehiculo() {
        // Encontrar el contenedor del campo vehículo
        const vehiculoContainer = this.vehiculoSelect.closest('.form-row, .fieldBox, .form-group, div');
        
        if (vehiculoContainer) {
            // Verificar si ya existe un tooltip
            let tooltip = vehiculoContainer.querySelector('.vehiculo-tooltip');
            
            if (!tooltip) {
                // Crear tooltip informativo
                tooltip = document.createElement('div');
                tooltip.className = 'vehiculo-tooltip';
                tooltip.textContent = 'El vehículo se carga automáticamente según el conductor seleccionado';
                tooltip.style.cssText = `
                    font-size: 11px;
                    color: #6c757d;
                    margin-top: 4px;
                    font-style: italic;
                    display: block;
                `;
                
                // Insertar después del select
                vehiculoContainer.appendChild(tooltip);
            }
            
            // También añadir un icono de información junto al label si existe
            const label = vehiculoContainer.querySelector('label');
            if (label) {
                // Verificar si ya tiene el icono
                if (!label.querySelector('.info-icon')) {
                    const infoIcon = document.createElement('span');
                    infoIcon.className = 'info-icon';
                    infoIcon.textContent = ' ⓘ';
                    infoIcon.title = 'Campo automático - Se selecciona según el conductor';
                    infoIcon.style.cssText = `
                        color: #17a2b8;
                        cursor: help;
                        font-size: 12px;
                        margin-left: 5px;
                    `;
                    label.appendChild(infoIcon);
                }
            }
        }
    }
    
    buscarCampo(nombres) {
        for (const nombre of nombres) {
            // Buscar por ID
            let elemento = document.getElementById(`id_${nombre}`);
            if (elemento) return elemento;
            
            elemento = document.getElementById(nombre);
            if (elemento) return elemento;
            
            // Buscar por name
            elemento = document.querySelector(`[name="${nombre}"]`);
            if (elemento) return elemento;
            
            elemento = document.querySelector(`[name*="${nombre}"]`);
            if (elemento) return elemento;
            
            // Buscar por label
            const label = document.querySelector(`label[for*="${nombre}"]`);
            if (label && label.htmlFor) {
                elemento = document.getElementById(label.htmlFor);
                if (elemento) return elemento;
            }
        }
        
        return null;
    }
    
    crearCampoVehiculo() {
        const conductorContainer = this.conductorSelect.closest('.form-row, .fieldBox, .form-group, div');
        
        if (conductorContainer) {
            // Crear un select para el vehículo (ahora será visible)
            this.vehiculoSelect = document.createElement('select');
            this.vehiculoSelect.id = 'vehiculo_asignado';
            this.vehiculoSelect.name = 'vehiculo';
            this.vehiculoSelect.className = 'vTextField'; // Para que coincida con estilos de Django Admin
            
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = '-- Seleccionar conductor primero --';
            this.vehiculoSelect.appendChild(emptyOption);
            
            // Buscar dónde insertar el campo (normalmente después del conductor)
            const conductorRow = conductorContainer.closest('.form-row');
            if (conductorRow) {
                // Crear una nueva fila para el vehículo
                const vehiculoRow = document.createElement('div');
                vehiculoRow.className = 'form-row';
                
                // Crear estructura similar a Django Admin
                const vehiculoField = document.createElement('div');
                vehiculoField.className = 'fieldBox';
                
                // Crear label
                const label = document.createElement('label');
                label.htmlFor = this.vehiculoSelect.id;
                label.textContent = 'Vehículo:';
                label.style.fontWeight = 'bold';
                
                vehiculoField.appendChild(label);
                vehiculoField.appendChild(this.vehiculoSelect);
                vehiculoRow.appendChild(vehiculoField);
                
                // Insertar después de la fila del conductor
                conductorRow.parentNode.insertBefore(vehiculoRow, conductorRow.nextSibling);
            } else {
                // Insertar después del conductor si no hay estructura de filas
                conductorContainer.parentNode.insertBefore(this.vehiculoSelect, conductorContainer.nextSibling);
            }
            
            // También crear un campo hidden para enviar el valor
            const hiddenInput = document.createElement('input');
            hiddenInput.type = 'hidden';
            hiddenInput.id = 'vehiculo_id_hidden';
            hiddenInput.name = 'vehiculo';
            conductorContainer.parentNode.insertBefore(hiddenInput, conductorContainer.nextSibling);
            
            console.log('Campo vehículo creado dinámicamente');
        }
    }
    
    configurarEventos() {
        // Evento para cambios en el conductor
        this.conductorSelect.addEventListener('change', (e) => {
            this.onConductorChange(e);
        });
        
        // Evento para cambios en el vehículo (aunque esté deshabilitado)
        if (this.vehiculoSelect) {
            // Remover cualquier listener anterior para evitar cambios manuales
            this.vehiculoSelect.replaceWith(this.vehiculoSelect.cloneNode(true));
            
            // Volver a obtener la referencia
            this.vehiculoSelect = document.getElementById(this.vehiculoSelect.id) || 
                                 document.querySelector('[name="vehiculo"]');
            
            // Aplicar estilos de solo lectura nuevamente
            this.hacerVehiculoSoloLectura();
        }
        
        // Evento para cambios en el estado
        if (this.estadoSelect) {
            this.estadoSelect.addEventListener('change', (e) => {
                this.onEstadoChange(e);
            });
        }
    }
    
    onConductorChange(event) {
        const conductorId = this.conductorSelect.value;
        const conductorNombre = this.conductorSelect.options[this.conductorSelect.selectedIndex].text;
        
        console.log(`Conductor cambiado: ${conductorId} - ${conductorNombre}`);
        
        // Guardar el vehículo original
        if (conductorId) {
            this.vehiculoOriginal = this.vehiculoSelect ? this.vehiculoSelect.value : '';
        }
        
        // Cargar el vehículo del conductor
        this.cargarVehiculoConductor(conductorId);
    }
    
    onVehiculoChange(event) {
        // Este evento ya no se usará ya que el campo es de solo lectura
        console.log('Intento de cambio en vehículo (campo de solo lectura)');
    }
    
    onEstadoChange(event) {
        // Si ya está programado y hay conductor y vehículo, mantenerlo
        const estadoActual = this.estadoSelect.options[this.estadoSelect.selectedIndex].text;
        if (estadoActual.toLowerCase().includes('programado') && 
            this.conductorSelect.value && 
            this.vehiculoSelect && this.vehiculoSelect.value) {
            
            setTimeout(() => {
                this.cambiarEstadoProgramado();
            }, 100);
        }
    }
    
    async cargarVehiculoConductor(conductorId) {
        if (!conductorId) {
            this.resetearVehiculo();
            return;
        }
        
        this.mostrarCargando();
        
        try {
            const response = await fetch(`${this.apiBaseUrl}conductor/listar?conductor_id=${conductorId}`);
            
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            
            this.ocultarCargando();
            
            if (data.error) {
                this.mostrarMensaje(data.error, 'error');
                this.resetearVehiculo();
            } else {
                this.actualizarVehiculo(data.data[0].vehiculo_id, data.data[0].vehiculo_id?.alias, data.data[0].vehiculo_display);
                
                if (data.data[0].vehiculo_id && conductorId) {
                    this.cambiarEstadoProgramado();
                }
            }
        } catch (error) {
            console.error('Error al cargar vehículo:', error);
            this.ocultarCargando();
            this.mostrarMensaje('Error al cargar el vehículo del conductor', 'error');
            this.resetearVehiculo();
        }
    }
    
    actualizarVehiculo(vehiculoId, alias, displayText) {
        if (!this.vehiculoSelect) return;
        
        // Limpiar opciones existentes
        while (this.vehiculoSelect.options.length > 0) {
            this.vehiculoSelect.remove(0);
        }
        
        // Crear nueva opción
        if (vehiculoId) {
            const nuevaOpcion = document.createElement('option');
            nuevaOpcion.value = vehiculoId;
            nuevaOpcion.textContent = displayText || `${alias}`;
            nuevaOpcion.selected = true;
            this.vehiculoSelect.appendChild(nuevaOpcion);
        } else {
            // Si no hay vehículo, mostrar mensaje
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = '-- Este conductor no tiene vehículo asignado --';
            this.vehiculoSelect.appendChild(emptyOption);
        }
        
        // Actualizar campo hidden
        const hiddenInput = document.getElementById('vehiculo_id_hidden');
        if (hiddenInput) {
            hiddenInput.value = vehiculoId || '';
        }
    }
    
    resetearVehiculo() {
        if (!this.vehiculoSelect) return;
        
        // Limpiar opciones
        while (this.vehiculoSelect.options.length > 0) {
            this.vehiculoSelect.remove(0);
        }
        
        // Añadir opción por defecto
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-- Seleccione un conductor --';
        this.vehiculoSelect.appendChild(defaultOption);
        
        // Limpiar campo hidden
        const hiddenInput = document.getElementById('vehiculo_id_hidden');
        if (hiddenInput) {
            hiddenInput.value = '';
        }
    }
    
    cambiarEstadoProgramado() {
        if (!this.estadoSelect) return;
        
        // Buscar opción "Programado"
        for (let option of this.estadoSelect.options) {
            if (option.text.toLowerCase().includes('programado') || 
                option.value.toLowerCase().includes('programado')) {
                
                this.estadoSelect.value = option.value;
                break;
            }
        }
    }
    
    mostrarCargando() {
        const container = this.conductorSelect.closest('.form-row, .fieldBox, .form-group, div');
        if (container) {
            const loadingSpan = document.createElement('span');
            loadingSpan.id = 'cargando-vehiculo';
            loadingSpan.textContent = ' Cargando vehículo...';
            loadingSpan.style.cssText = `
                margin-left: 10px;
                font-size: 12px;
                color: #6c757d;
                font-style: italic;
            `;
            
            container.appendChild(loadingSpan);
        }
    }
    
    ocultarCargando() {
        const loadingSpan = document.getElementById('cargando-vehiculo');
        if (loadingSpan) {
            loadingSpan.remove();
        }
    }
    
    mostrarMensaje(texto, tipo = 'info') {
        console.log(`[${tipo.toUpperCase()}] ${texto}`);
        
        // Colores según tipo
        const colores = {
            info: { bg: '#d1ecf1', color: '#0c5460', border: '#bee5eb' },
            success: { bg: '#d4edda', color: '#155724', border: '#c3e6cb' },
            error: { bg: '#f8d7da', color: '#721c24', border: '#f5c6cb' },
            warning: { bg: '#fff3cd', color: '#856404', border: '#ffeaa7' }
        };
        
        const color = colores[tipo] || colores.info;
        
        const mensaje = document.createElement('div');
        mensaje.className = `asignacion-mensaje ${tipo}`;
        mensaje.textContent = texto;
        mensaje.style.cssText = `
            margin: 10px 0;
            padding: 10px;
            background-color: ${color.bg};
            color: ${color.color};
            border: 1px solid ${color.border};
            border-radius: 4px;
            font-size: 14px;
        `;
        
        // Buscar donde insertar el mensaje
        const firstFieldset = document.querySelector('fieldset');
        const container = document.getElementById('asignacion-mensajes');
        
        if (container) {
            container.appendChild(mensaje);
        } else if (firstFieldset) {
            const newContainer = document.createElement('div');
            newContainer.id = 'asignacion-mensajes';
            firstFieldset.parentNode.insertBefore(newContainer, firstFieldset);
            newContainer.appendChild(mensaje);
        } else {
            // Insertar al principio del formulario
            const form = this.conductorSelect.closest('form');
            if (form) {
                form.insertBefore(mensaje, form.firstChild);
            }
        }
        
        // Auto-eliminar después de 5 segundos
        setTimeout(() => {
            mensaje.style.opacity = '0';
            mensaje.style.transition = 'opacity 0.3s';
            setTimeout(() => {
                mensaje.remove();
                // Eliminar contenedor si está vacío
                const container = document.getElementById('asignacion-mensajes');
                if (container && container.children.length === 0) {
                    container.remove();
                }
            }, 300);
        }, 5000);
    }
    
    procesarValoresIniciales() {
        // Si ya hay un conductor seleccionado, cargar su vehículo
        if (this.conductorSelect.value) {
            setTimeout(() => {
                this.cargarVehiculoConductor(this.conductorSelect.value);
            }, 800);
        } else if (this.vehiculoSelect) {
            // Si no hay conductor, asegurar que el vehículo esté en estado inicial
            this.resetearVehiculo();
        }
        
        // Si ya hay conductor y vehículo, asegurar estado programado
        if (this.conductorSelect.value && this.vehiculoSelect && this.vehiculoSelect.value) {
            setTimeout(() => {
                this.cambiarEstadoProgramado();
            }, 1000);
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    new PedidoAsignacion();
});