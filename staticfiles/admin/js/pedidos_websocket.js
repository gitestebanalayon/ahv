// static/admin/js/pedidos_websocket_simple.js
(function() {
    'use strict';
    
    console.log('🔌 Inicializando WebSocket para pedidos...');
    
    // Solo ejecutar en la página de listado de pedidos del admin
    if (!window.location.pathname.includes('/admin/sistema/pedido') ||
        window.location.pathname.includes('/add/') ||
        window.location.pathname.includes('/change/') ||
        window.location.pathname.includes('/delete/')) {
        return;
    }
    
    // Configurar URL WebSocket - IMPORTANTE: usar wss:// para HTTPS
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    const wsUrl = `${protocol}//${host}/ws/pedidos/`;
    
    console.log(`Conectando a: ${wsUrl}`);
    
    let socket = null;
    let reconnectAttempts = 0;
    const maxReconnectAttempts = 5;
    const reconnectDelay = 3000;
    
    function connect() {
        try {
            socket = new WebSocket(wsUrl);
            
            socket.onopen = function() {
                console.log('✅ WebSocket conectado');
                reconnectAttempts = 0;
                
                // Suscribirse a actualizaciones
                socket.send(JSON.stringify({
                    type: 'subscribe',
                    page: 'admin'
                }));
            };
            
            socket.onmessage = function(event) {
                try {
                    const data = JSON.parse(event.data);
                    handleWebSocketMessage(data);
                } catch (error) {
                    console.error('Error parseando mensaje:', error);
                }
            };
            
            socket.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
            
            socket.onclose = function(event) {
                console.log('WebSocket cerrado:', event.code, event.reason);
                
                // Intentar reconectar si no fue un cierre intencional
                if (event.code !== 1000 && reconnectAttempts < maxReconnectAttempts) {
                    reconnectAttempts++;
                    console.log(`Reintentando conexión en ${reconnectDelay}ms (intento ${reconnectAttempts})`);
                    setTimeout(connect, reconnectDelay);
                }
            };
            
        } catch (error) {
            console.error('Error creando WebSocket:', error);
        }
    }
    
    function handleWebSocketMessage(data) {
        switch(data.type) {
            case 'pedido_created':
                console.log('Nuevo pedido:', data.pedido.codigo_pedido);
                showNotification(data.pedido);
                refreshTable();
                break;
                
            case 'pedido_updated':
                console.log('Pedido actualizado:', data.pedido.codigo_pedido);
                refreshTable();
                break;
                
            case 'connection_established':
                console.log('Conexión establecida:', data.message);
                break;
        }
    }
    
    function showNotification(pedido) {
        // Notificación simple usando alert de Django si está disponible
        if (typeof django !== 'undefined' && django.jQuery) {
            const $ = django.jQuery;
            
            // Crear notificación estilo toast
            const toast = $(`
                <div class="websocket-notification" style="
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    background: var(--primary);
                    color: white;
                    padding: 15px;
                    border-radius: 8px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
                    z-index: 9999;
                    max-width: 300px;
                    animation: slideIn 0.3s ease;
                ">
                    <div style="font-weight: bold; margin-bottom: 5px;">
                        <span style="margin-right: 8px;">📦</span>
                        Nuevo Pedido
                    </div>
                    <div style="font-size: 14px;">
                        <strong>${pedido.codigo_pedido}</strong><br>
                        Cliente: ${pedido.cliente}<br>
                        Yardas: ${pedido.cantidad_yardas}
                    </div>
                </div>
            `);
            
            $('body').append(toast);
            
            // Auto-eliminar después de 5 segundos
            setTimeout(() => {
                toast.fadeOut(300, function() {
                    $(this).remove();
                });
            }, 5000);
        }
    }
    
    function refreshTable() {
        // Refrescar la tabla usando la API de Django Admin
        const changelistForm = document.getElementById('changelist-form');
        if (changelistForm) {
            // Simular clic en el botón de búsqueda para refrescar
            const searchButton = document.querySelector('input[name="_search"]');
            if (searchButton) {
                searchButton.click();
            } else {
                // Fallback: recargar la página
                setTimeout(() => {
                    window.location.reload();
                }, 1000);
            }
        }
    }
    
    // Iniciar conexión cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', connect);
    } else {
        connect();
    }
    
    // Estilos CSS
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from {
                transform: translateX(100%);
                opacity: 0;
            }
            to {
                transform: translateX(0);
                opacity: 1;
            }
        }
        
        .websocket-notification {
            border-left: 4px solid #4CAF50;
        }
    `;
    document.head.appendChild(style);
    
})();