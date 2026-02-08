// static/admin/js/pedidos_pusher.js
class PedidosPusher {
    constructor() {
        this.pusher = null;
        this.channel = null;
        this.initialized = false;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        this.initialize();
    }
    
    initialize() {
        console.log('🚀 Inicializando sistema de notificaciones con Pusher');
        
        // Determinar si estamos en producción o desarrollo
        this.isProduction = window.location.hostname.includes('pythonanywhere.com');
        
        if (this.isProduction) {
            console.log('📍 Entorno: PythonAnywhere (Producción)');
            this.initPusher();
        } else {
            console.log('📍 Entorno: Desarrollo local');
            this.initLocalWebSocket();
        }
    }
    
    initPusher() {
        // Cargar Pusher dinámicamente si no está cargado
        if (typeof Pusher === 'undefined') {
            this.loadPusherLibrary();
        } else {
            this.connectPusher();
        }
    }
    
    loadPusherLibrary() {
        console.log('📦 Cargando biblioteca Pusher...');
        
        const script = document.createElement('script');
        script.src = 'https://js.pusher.com/7.2/pusher.min.js';
        script.async = true;
        
        script.onload = () => {
            console.log('✅ Pusher cargado exitosamente');
            this.connectPusher();
        };
        
        script.onerror = (error) => {
            console.error('❌ Error cargando Pusher:', error);
            this.fallbackToPolling();
        };
        
        document.head.appendChild(script);
    }
    
    connectPusher() {
        try {
            // Configuración de Pusher
            this.pusher = new Pusher('TU_PUSHER_KEY_AQUI', {  // ¡Reemplaza con tu key!
                cluster: 'us2',
                forceTLS: true,
                authEndpoint: '/pusher/auth/',  // Opcional: para canales privados
                enabledTransports: ['ws', 'wss'],
                disabledTransports: ['xhr_streaming', 'xhr_polling']
            });
            
            // Manejar eventos de conexión
            this.pusher.connection.bind('connected', () => {
                console.log('✅ Conectado a Pusher');
                this.reconnectAttempts = 0;
                this.subscribeToChannel();
            });
            
            this.pusher.connection.bind('disconnected', () => {
                console.log('🔌 Desconectado de Pusher');
                this.handleReconnection();
            });
            
            this.pusher.connection.bind('error', (err) => {
                console.error('❌ Error de conexión Pusher:', err);
            });
            
            console.log('🔗 Conectando a Pusher...');
            
        } catch (error) {
            console.error('❌ Error inicializando Pusher:', error);
            this.fallbackToPolling();
        }
    }
    
    subscribeToChannel() {
        try {
            // Suscribirse al canal público
            this.channel = this.pusher.subscribe('pedidos-channel');
            
            // Escuchar eventos
            this.channel.bind('pedido-created', (data) => {
                console.log('📦 Nuevo pedido recibido:', data);
                this.handleNewPedido(data.pedido);
            });
            
            this.channel.bind('pedido-updated', (data) => {
                console.log('✏️ Pedido actualizado:', data);
                this.handleUpdatedPedido(data.pedido);
            });
            
            this.channel.bind('subscription_succeeded', () => {
                console.log('✅ Suscrito al canal de pedidos');
                this.showConnectionStatus('connected');
            });
            
            this.channel.bind('subscription_error', (error) => {
                console.error('❌ Error suscribiéndose al canal:', error);
            });
            
        } catch (error) {
            console.error('❌ Error suscribiéndose al canal:', error);
        }
    }
    
    initLocalWebSocket() {
        // Para desarrollo local: usar WebSocket nativo
        console.log('🔗 Conectando a WebSocket local...');
        
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${protocol}//${window.location.host}/ws/pedidos/`;
        
        this.ws = new WebSocket(wsUrl);
        
        this.ws.onopen = () => {
            console.log('✅ WebSocket local conectado');
            this.ws.send(JSON.stringify({ type: 'subscribe' }));
        };
        
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === 'pedido_created') {
                    this.handleNewPedido(data.pedido);
                }
            } catch (error) {
                console.error('Error procesando mensaje:', error);
            }
        };
        
        this.ws.onerror = (error) => {
            console.error('Error WebSocket:', error);
        };
    }
    
    handleNewPedido(pedido) {
        console.log(`🟠 ¡NUEVO PEDIDO! ${pedido.codigo_pedido}`);
        
        // 1. Mostrar notificación
        this.showNotification(pedido);
        
        // 2. Refrescar tabla
        this.refreshAdminTable();
        
        // 3. Resaltar en la interfaz
        this.highlightNewRow(pedido.id);
    }
    
    handleUpdatedPedido(pedido) {
        console.log(`✏️ Pedido actualizado: ${pedido.codigo_pedido}`);
        this.refreshAdminTable();
    }
    
    showNotification(pedido) {
        if (typeof Swal !== 'undefined') {
            const backgroundColor = this.isProduction ? '#1a237e' : '#ffffff';
            const textColor = this.isProduction ? '#ffffff' : '#333333';
            
            Swal.fire({
                toast: true,
                position: 'bottom-end',
                html: `
                    <div style="color: ${textColor};">
                        <div style="font-weight: bold; margin-bottom: 8px; font-size: 16px;">
                            🚚 ¡Nuevo Pedido!
                        </div>
                        <div style="margin-bottom: 4px;">
                            <strong>Orden:</strong> ${pedido.codigo_pedido}
                        </div>
                        <div style="margin-bottom: 4px;">
                            <strong>Cliente:</strong> ${pedido.cliente}
                        </div>
                        <div style="margin-bottom: 4px;">
                            <strong>Yardas:</strong> ${pedido.cantidad_yardas}
                        </div>
                        <div>
                            <strong>Total:</strong> $${pedido.precio_total ? parseFloat(pedido.precio_total).toFixed(2) : '0.00'}
                        </div>
                    </div>
                `,
                background: backgroundColor,
                showConfirmButton: false,
                timer: 5000,
                timerProgressBar: true,
                width: '350px',
                padding: '16px',
                customClass: {
                    popup: 'pedido-notification'
                },
                didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer);
                    toast.addEventListener('mouseleave', Swal.resumeTimer);
                }
            });
        }
    }
    
    refreshAdminTable() {
        console.log('🔄 Refrescando tabla de administración...');
        
        const changelist = document.querySelector('#changelist');
        if (!changelist) return;
        
        // Usar AJAX para refrescar solo la tabla
        const url = `${window.location.pathname}?ajax=1&_=${Date.now()}`;
        
        fetch(url)
            .then(response => response.text())
            .then(html => {
                const temp = document.createElement('div');
                temp.innerHTML = html;
                const newTable = temp.querySelector('#changelist');
                
                if (newTable) {
                    // Preservar checkboxes seleccionados
                    const selected = Array.from(
                        changelist.querySelectorAll('input[type="checkbox"]:checked')
                    ).map(cb => cb.value);
                    
                    changelist.innerHTML = newTable.innerHTML;
                    
                    // Restaurar selecciones
                    selected.forEach(id => {
                        const checkbox = changelist.querySelector(`input[type="checkbox"][value="${id}"]`);
                        if (checkbox) checkbox.checked = true;
                    });
                    
                    console.log('✅ Tabla actualizada');
                }
            })
            .catch(error => {
                console.error('Error refrescando tabla:', error);
            });
    }
    
    highlightNewRow(pedidoId) {
        // Buscar y resaltar la fila del nuevo pedido
        setTimeout(() => {
            const rows = document.querySelectorAll('#result_list tr');
            rows.forEach(row => {
                if (row.textContent.includes(pedidoId)) {
                    row.classList.add('new-pedido-highlight');
                    setTimeout(() => {
                        row.classList.remove('new-pedido-highlight');
                    }, 5000);
                }
            });
        }, 1000);
    }
    
    showConnectionStatus(status) {
        // Crear o actualizar indicador de estado
        let statusEl = document.getElementById('pusher-status');
        
        if (!statusEl) {
            statusEl = document.createElement('div');
            statusEl.id = 'pusher-status';
            statusEl.style.cssText = `
                position: fixed;
                bottom: 10px;
                right: 10px;
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
                z-index: 9999;
                font-family: monospace;
                opacity: 0.9;
            `;
            document.body.appendChild(statusEl);
        }
        
        if (status === 'connected') {
            statusEl.textContent = '🟢 Notificaciones activas';
            statusEl.style.backgroundColor = '#10b981';
            statusEl.style.color = 'white';
        } else {
            statusEl.textContent = '🔴 Notificaciones inactivas';
            statusEl.style.backgroundColor = '#ef4444';
            statusEl.style.color = 'white';
        }
    }
    
    handleReconnection() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Intentando reconexión ${this.reconnectAttempts}/${this.maxReconnectAttempts}...`);
            
            setTimeout(() => {
                this.connectPusher();
            }, 3000 * this.reconnectAttempts); // Backoff exponencial
        } else {
            console.error('❌ Máximo de intentos alcanzado. Cambiando a polling.');
            this.fallbackToPolling();
        }
    }
    
    fallbackToPolling() {
        console.log('🔄 Cambiando a sistema de polling...');
        this.showConnectionStatus('polling');
        
        // Implementar polling cada 10 segundos
        this.pollingInterval = setInterval(() => {
            this.checkPedidosViaAPI();
        }, 10000);
    }
    
    async checkPedidosViaAPI() {
        try {
            const response = await fetch('/api/pedidos/latest/');
            const data = await response.json();
            
            if (data.nuevos && data.nuevos.length > 0) {
                data.nuevos.forEach(pedido => {
                    this.handleNewPedido(pedido);
                });
            }
        } catch (error) {
            console.error('Error en polling:', error);
        }
    }
    
    destroy() {
        // Limpiar recursos
        if (this.pusher) {
            this.pusher.disconnect();
        }
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
        }
    }
}

// Estilos CSS
const pusherStyles = `
    .new-pedido-highlight {
        animation: highlight-pulse 2s ease-in-out;
        background-color: rgba(255, 193, 7, 0.2) !important;
    }
    
    @keyframes highlight-pulse {
        0% { background-color: rgba(255, 193, 7, 0.4); }
        50% { background-color: rgba(255, 193, 7, 0.2); }
        100% { background-color: rgba(255, 193, 7, 0.1); }
    }
    
    .pedido-notification {
        border-left: 4px solid #f08227 !important;
    }
    
    .dark .pedido-notification {
        background: #1a237e !important;
        color: white !important;
    }
`;

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    // Añadir estilos
    const styleEl = document.createElement('style');
    styleEl.textContent = pusherStyles;
    document.head.appendChild(styleEl);
    
    // Inicializar Pusher solo en páginas de pedidos
    const path = window.location.pathname;
    if (path.includes('/admin/sistema/pedido') && 
        !path.includes('/add/') && 
        !path.includes('/change/') &&
        !path.includes('/delete/')) {
        
        console.log('📍 Página de listado de pedidos detectada');
        window.pedidosNotifier = new PedidosPusher();
        
        // Limpiar al salir de la página
        window.addEventListener('beforeunload', () => {
            if (window.pedidosNotifier) {
                window.pedidosNotifier.destroy();
            }
        });
    }
});