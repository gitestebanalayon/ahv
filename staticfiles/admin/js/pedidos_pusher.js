// static/admin/js/pedidos_pusher.js - VERSIÓN CORREGIDA
class PedidosPusher {
    constructor() {
        this.pusher = null;
        this.channel = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
        
        console.log('🚀 Inicializando Pusher para notificaciones de pedidos');
        this.initialize();
    }
    
    initialize() {
        // Usar Pusher SIEMPRE, tanto en desarrollo como producción
        this.initPusher();
    }
    
    initPusher() {
        // Cargar Pusher desde CDN si no está disponible
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
            this.showFallbackMessage();
        };
        
        document.head.appendChild(script);
    }
    
    connectPusher() {
        try {
            // ¡IMPORTANTE! Usa TU clave de Pusher aquí
            const PUSHER_KEY = '7b9e25f3884835405cf2';
            
            this.pusher = new Pusher(PUSHER_KEY, {
                cluster: 'mt1',  // ← Tu cluster
                forceTLS: true,
                enabledTransports: ['ws', 'wss'],
                authEndpoint: '/pusher/auth/',  // Opcional
                auth: {
                    headers: {
                        'X-CSRFToken': this.getCookie('csrftoken')
                    }
                }
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
            
            console.log('🔗 Conectando a Pusher (cluster: mt1)...');
            
        } catch (error) {
            console.error('❌ Error inicializando Pusher:', error);
            this.handleReconnection();
        }
    }
    
    subscribeToChannel() {
        try {
            // Suscribirse al canal de pedidos
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
                console.log('✅ Suscrito al canal "pedidos-channel"');
                this.showConnectionStatus(true);
            });
            
            this.channel.bind('subscription_error', (error) => {
                console.error('❌ Error suscribiéndose al canal:', error);
            });
            
        } catch (error) {
            console.error('❌ Error suscribiéndose al canal:', error);
        }
    }
    
    handleNewPedido(pedido) {
        console.log(`🟠 ¡NUEVO PEDIDO! ${pedido.codigo_pedido}`);
        
        // 1. Mostrar notificación
        this.showNotification(pedido);
        
        // 2. Refrescar tabla
        this.refreshAdminTable();
        
        // 3. Resaltar nueva fila
        this.highlightNewRow(pedido.id);
    }
    
    showNotification(pedido) {
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                toast: true,
                position: 'bottom-end',
                html: `
                    <div>
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
        console.log('🔄 Refrescando tabla...');
        
        const changelist = document.querySelector('#changelist');
        if (!changelist) return;
        
        const url = `${window.location.pathname}?ajax=1&_=${Date.now()}`;
        
        fetch(url)
            .then(response => response.text())
            .then(html => {
                const temp = document.createElement('div');
                temp.innerHTML = html;
                const newTable = temp.querySelector('#changelist');
                
                if (newTable) {
                    // Preservar selecciones
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
    
    handleReconnection() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            console.log(`🔄 Reconectando... ${this.reconnectAttempts}/${this.maxReconnectAttempts}`);
            
            setTimeout(() => {
                this.connectPusher();
            }, 3000 * this.reconnectAttempts);
        } else {
            console.error('❌ Máximo de intentos alcanzado');
            this.showFallbackMessage();
        }
    }
    
    showConnectionStatus(connected) {
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
        
        if (connected) {
            statusEl.textContent = '🟢 Notificaciones activas';
            statusEl.style.backgroundColor = '#10b981';
            statusEl.style.color = 'white';
        } else {
            statusEl.textContent = '🔴 Notificaciones inactivas';
            statusEl.style.backgroundColor = '#ef4444';
            statusEl.style.color = 'white';
        }
    }
    
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    
    showFallbackMessage() {
        console.log('⚠️ Pusher no disponible');
        // Aquí puedes implementar polling si lo necesitas
    }
}

// Estilos CSS
const addPusherStyles = () => {
    const styleEl = document.createElement('style');
    styleEl.textContent = `
        .pedido-notification {
            border-left: 4px solid #f08227 !important;
        }
        
        .new-pedido-highlight {
            animation: highlight-pulse 2s ease-in-out;
            background-color: rgba(255, 193, 7, 0.2) !important;
        }
        
        @keyframes highlight-pulse {
            0% { background-color: rgba(255, 193, 7, 0.4); }
            50% { background-color: rgba(255, 193, 7, 0.2); }
            100% { background-color: rgba(255, 193, 7, 0.1); }
        }
    `;
    document.head.appendChild(styleEl);
};

// Inicializar automáticamente
const initializePusherForPedidos = () => {
    const path = window.location.pathname;
    const isPedidosListPage = path.includes('/admin/sistema/pedido') && 
                              !path.includes('/add/') && 
                              !path.includes('/change/') &&
                              !path.includes('/delete/');
    
    if (isPedidosListPage) {
        console.log('📍 Página de listado de pedidos detectada');
        addPusherStyles();
        window.pedidosPusher = new PedidosPusher();
    }
};

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePusherForPedidos);
} else {
    initializePusherForPedidos();
}