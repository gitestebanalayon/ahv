// static/admin/js/pedido_asignacion_simple.js

class PedidoAsignacion {
    constructor() {
        this.conductorSelect = null;
        this.vehiculoSelect = null;
        this.apiBaseUrl = 'http://127.0.0.1:8000/';
        this.initialized = false;
        
        this.init();
    }
    
    init() {
        console.log('Inicializando sistema de asignación de vehículo');
        
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.inicializarComponentes());
        } else {
            this.inicializarComponentes();
        }
    }
    
    inicializarComponentes() {
        const intentosMaximos = 5;
        let intento = 0;
        
        const buscarCampos = () => {
            intento++;
            console.log(`Intento ${intento} de encontrar campos...`);
            
            this.encontrarCampos();
            
            if (this.conductorSelect) {
                console.log('Campos encontrados:', {
                    conductor: this.conductorSelect,
                    vehiculo: this.vehiculoSelect
                });
                
                this.configurarEventos();
                this.procesarValoresIniciales();
                this.initialized = true;
            } else if (intento < intentosMaximos) {
                setTimeout(buscarCampos, 500);
            } else {
                console.warn('No se encontró el campo conductor después de varios intentos');
            }
        };
        
        setTimeout(buscarCampos, 300);
    }
    
    encontrarCampos() {
        this.conductorSelect = this.buscarCampo(['id_conductor', 'conductor', 'conductor-select']);
        this.vehiculoSelect = this.buscarCampo(['id_vehiculo', 'vehiculo', 'vehiculo-select']);
        
        console.log('Resultados de búsqueda:', {
            conductor: this.conductorSelect?.id || this.conductorSelect?.name,
            vehiculo: this.vehiculoSelect?.id || this.vehiculoSelect?.name
        });
        
        if (!this.vehiculoSelect) {
            this.buscarCamposPorEstructura();
        }
        
        if (!this.vehiculoSelect && this.conductorSelect) {
            this.crearCampoVehiculo();
        }
        
        this.hacerVehiculoSoloLectura();
    }
    
    buscarCamposPorEstructura() {
        const posiblesNombres = ['vehiculo', 'vehiculo_id', 'id_vehiculo'];
        
        for (const nombre of posiblesNombres) {
            let elemento = document.querySelector(`input[name="${nombre}"]`);
            if (elemento && elemento.type === 'hidden') {
                console.log('Encontrado campo hidden para vehículo:', elemento);
                this.crearSelectDesdeHidden(elemento);
                return;
            }
            
            elemento = document.querySelector(`select[name="${nombre}"]`);
            if (elemento) {
                this.vehiculoSelect = elemento;
                console.log('Encontrado select para vehículo:', elemento);
                return;
            }
        }
        
        const labels = document.querySelectorAll('label');
        for (const label of labels) {
            if (label.textContent.toLowerCase().includes('vehículo') || 
                label.textContent.toLowerCase().includes('vehiculo')) {
                if (label.htmlFor) {
                    const elemento = document.getElementById(label.htmlFor);
                    if (elemento) {
                        this.vehiculoSelect = elemento;
                        console.log('Encontrado vehículo por label:', elemento);
                        return;
                    }
                }
            }
        }
    }
    
    crearSelectDesdeHidden(hiddenInput) {
        const container = hiddenInput.closest('.form-row, .fieldBox, .form-group, div') || 
                          hiddenInput.parentElement;
        
        if (container) {
            this.vehiculoSelect = document.createElement('select');
            this.vehiculoSelect.name = 'vehiculo';
            this.vehiculoSelect.id = 'vehiculo_asignado_' + Date.now();
            this.vehiculoSelect.className = 'vTextField';
            
            const defaultOption = document.createElement('option');
            defaultOption.value = '';
            defaultOption.textContent = '-- Seleccionar conductor primero --';
            this.vehiculoSelect.appendChild(defaultOption);
            
            container.insertBefore(this.vehiculoSelect, hiddenInput);
            
            this.vehiculoSelect.addEventListener('change', () => {
                hiddenInput.value = this.vehiculoSelect.value;
            });
            
            console.log('Select creado desde hidden input');
        }
    }
    
    hacerVehiculoSoloLectura() {
        if (this.vehiculoSelect) {
            // Deshabilitar el campo select (pero que se envíe el valor)
            this.vehiculoSelect.disabled = false;
            
            // Prevenir cambios manuales
            this.vehiculoSelect.addEventListener('mousedown', (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
            
            this.vehiculoSelect.addEventListener('keydown', (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
            
            this.agregarTooltipVehiculo();
            
            console.log('Campo vehículo configurado como solo lectura visual');
        }
    }
    
    agregarTooltipVehiculo() {
        const vehiculoContainer = this.vehiculoSelect.closest('.form-row, .fieldBox, .form-group, div');
        
        if (vehiculoContainer) {
            let tooltip = vehiculoContainer.querySelector('.vehiculo-tooltip');
            
            if (!tooltip) {
                tooltip = document.createElement('div');
                tooltip.className = 'vehiculo-tooltip';
                tooltip.textContent = 'El vehículo se asigna automáticamente según el conductor seleccionado';
                tooltip.style.cssText = `
                    font-size: 11px;
                    color: #6c757d;
                    margin-top: 4px;
                    font-style: italic;
                    display: block;
                `;
                
                vehiculoContainer.appendChild(tooltip);
            }
            
            const label = vehiculoContainer.querySelector('label');
            if (label && !label.querySelector('.info-icon')) {
                const infoIcon = document.createElement('span');
                infoIcon.className = 'info-icon';
                infoIcon.textContent = ' ⓘ';
                infoIcon.title = 'Campo automático - Se actualiza según el conductor';
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
    
    buscarCampo(nombres) {
        for (const nombre of nombres) {
            let elemento = document.getElementById(nombre);
            if (elemento) return elemento;
            
            elemento = document.getElementById(`id_${nombre}`);
            if (elemento) return elemento;
            
            elemento = document.querySelector(`[name="${nombre}"]`);
            if (elemento) return elemento;
            
            elemento = document.querySelector(`[name*="${nombre}"]`);
            if (elemento) return elemento;
        }
        
        return null;
    }
    
    crearCampoVehiculo() {
        const conductorContainer = this.conductorSelect.closest('.form-row, .fieldBox, .form-group, div');
        
        if (conductorContainer) {
            this.vehiculoSelect = document.createElement('select');
            this.vehiculoSelect.id = 'vehiculo_asignado_' + Date.now();
            this.vehiculoSelect.name = 'vehiculo';
            this.vehiculoSelect.className = 'vTextField';
            
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = '-- Seleccionar conductor primero --';
            this.vehiculoSelect.appendChild(emptyOption);
            
            const conductorRow = conductorContainer.closest('.form-row');
            if (conductorRow) {
                const vehiculoRow = document.createElement('div');
                vehiculoRow.className = 'form-row';
                
                const vehiculoField = document.createElement('div');
                vehiculoField.className = 'fieldBox';
                
                const label = document.createElement('label');
                label.htmlFor = this.vehiculoSelect.id;
                label.textContent = 'Vehículo:';
                label.style.fontWeight = 'bold';
                
                vehiculoField.appendChild(label);
                vehiculoField.appendChild(this.vehiculoSelect);
                vehiculoRow.appendChild(vehiculoField);
                
                conductorRow.parentNode.insertBefore(vehiculoRow, conductorRow.nextSibling);
            } else {
                conductorContainer.parentNode.insertBefore(this.vehiculoSelect, conductorContainer.nextSibling);
            }
            
            console.log('Campo vehículo creado dinámicamente');
        }
    }
    
    configurarEventos() {
        // Evento para cambios en el conductor
        this.conductorSelect.addEventListener('change', (e) => {
            this.onConductorChange(e);
        });
        
        // También capturar el evento submit del formulario para validar
        const form = this.conductorSelect.closest('form');
        if (form) {
            form.addEventListener('submit', (e) => {
                this.antesDeEnviarFormulario(e);
            });
        }
    }
    
    onConductorChange(event) {
        const conductorId = this.conductorSelect.value;
        const conductorNombre = this.conductorSelect.options[this.conductorSelect.selectedIndex].text;
        
        console.log(`Conductor cambiado: ${conductorId} - ${conductorNombre}`);
        
        // Cargar el vehículo del conductor
        this.cargarVehiculoConductor(conductorId);
    }
    
    async cargarVehiculoConductor(conductorId) {
        if (!conductorId) {
            this.resetearVehiculo();
            return;
        }
        
        this.mostrarCargando();
        
        try {
            const url = `${this.apiBaseUrl}conductor/listar?conductor_id=${conductorId}`;
            console.log('Consultando API:', url);
            
            const response = await fetch(url);
            
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('Respuesta API:', data);
            
            this.ocultarCargando();
            
            if (data.error) {
                this.mostrarMensaje(data.error, 'error');
                this.resetearVehiculo();
            } else if (data.data && data.data.length > 0) {
                const conductorData = data.data[0];
                const vehiculoId = conductorData.vehiculo_id?.id;
                const vehiculoAlias = conductorData.vehiculo_id?.alias;
                const vehiculoDisplay = conductorData.vehiculo_display || 
                                       (vehiculoAlias ? `${vehiculoAlias}` : 'Sin vehículo asignado');
                
                this.actualizarVehiculo(vehiculoId, vehiculoDisplay);
            } else {
                this.mostrarMensaje('No se encontró información del conductor', 'warning');
                this.resetearVehiculo();
            }
        } catch (error) {
            console.error('Error al cargar vehículo:', error);
            this.ocultarCargando();
            this.mostrarMensaje('Error al cargar el vehículo del conductor', 'error');
            this.resetearVehiculo();
        }
    }
    
    actualizarVehiculo(vehiculoId, displayText) {
        if (!this.vehiculoSelect) return;
        
        // Limpiar opciones existentes
        while (this.vehiculoSelect.options.length > 0) {
            this.vehiculoSelect.remove(0);
        }
        
        // Crear nueva opción
        if (vehiculoId) {
            const nuevaOpcion = document.createElement('option');
            nuevaOpcion.value = vehiculoId;
            nuevaOpcion.textContent = displayText || 'Vehículo asignado';
            nuevaOpcion.selected = true;
            this.vehiculoSelect.appendChild(nuevaOpcion);
            
            // Mostrar mensaje informativo
            // this.mostrarMensaje(`Vehículo asignado: ${displayText}`, 'success');
        } else {
            const emptyOption = document.createElement('option');
            emptyOption.value = '';
            emptyOption.textContent = '-- Este conductor no tiene vehículo asignado --';
            this.vehiculoSelect.appendChild(emptyOption);
            
            console.log('Conductor sin vehículo asignado');
            this.mostrarMensaje('Este conductor no tiene vehículo asignado', 'warning');
        }
        
        // Forzar el cambio de evento para que Django detecte el valor
        this.vehiculoSelect.dispatchEvent(new Event('change', { bubbles: true }));
    }
    
    resetearVehiculo() {
        if (!this.vehiculoSelect) return;
        
        while (this.vehiculoSelect.options.length > 0) {
            this.vehiculoSelect.remove(0);
        }
        
        const defaultOption = document.createElement('option');
        defaultOption.value = '';
        defaultOption.textContent = '-- Seleccione un conductor --';
        this.vehiculoSelect.appendChild(defaultOption);
        
        console.log('Vehículo reseteado');
    }
    
    antesDeEnviarFormulario(event) {
        console.log('Validando formulario antes de enviar...');
        
        // Verificar que si hay conductor, también haya vehículo
        if (this.conductorSelect && this.conductorSelect.value && 
            this.vehiculoSelect && !this.vehiculoSelect.value) {
            
            event.preventDefault();
            this.mostrarMensaje('Debe seleccionar un conductor que tenga vehículo asignado', 'error');
            return false;
        }
        
        console.log('Formulario validado correctamente');
        return true;
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
        
        const colores = {
            info: { color: '#0c5460' },
            success: { color: '#155724' },
            error: { color: '#e72a3dff' },
            warning: { color: '#e72a3dff' }
        };
        
        const color = colores[tipo] || colores.info;
        
        const mensaje = document.createElement('div');
        mensaje.className = `asignacion-mensaje ${tipo}`;
        mensaje.textContent = texto;
        mensaje.style.cssText = `
            margin: 10px 0;
            padding: 10px;
            color: ${color.color};
            border-radius: 4px;
            font-size: 14px;
        `;
        
        const firstFieldset = document.querySelector('fieldset');
        const container = document.getElementById('asignacion-mensajes');
        
        if (container) {
            container.appendChild(mensaje);
        } else if (firstFieldset) {
            const newContainer = document.createElement('div');
            newContainer.id = 'asignacion-mensajes';
            firstFieldset.parentNode.insertBefore(newContainer, firstFieldset);
            newContainer.appendChild(mensaje);
        }
        
        setTimeout(() => {
            mensaje.style.opacity = '0';
            mensaje.style.transition = 'opacity 0.3s';
            setTimeout(() => {
                mensaje.remove();
                const container = document.getElementById('asignacion-mensajes');
                if (container && container.children.length === 0) {
                    container.remove();
                }
            }, 300);
        }, 5000);
    }
    
    procesarValoresIniciales() {
        // Si ya hay un conductor seleccionado al cargar la página
        if (this.conductorSelect && this.conductorSelect.value) {
            console.log('Procesando valores iniciales - Conductor ya seleccionado:', this.conductorSelect.value);
            
            setTimeout(() => {
                this.cargarVehiculoConductor(this.conductorSelect.value);
            }, 800);
        } else if (this.vehiculoSelect) {
            this.resetearVehiculo();
        }
    }
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.pedidoAsignacion = new PedidoAsignacion();
    });
} else {
    window.pedidoAsignacion = new PedidoAsignacion();
}