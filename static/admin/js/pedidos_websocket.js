// static/admin/js/pedidos_websocket.js

(function () {
    // Verificar más estrictamente si ya está inicializado
    const uniqueId = 'pedidosWebSocketSimple';
    if (window[uniqueId]) return;
    window[uniqueId] = true;

    // Verificar que estamos SOLO en la vista de cambio de pedidos
    const path = window.location.pathname;
    if (!path.includes('/admin/sistema/pedido') ||
        path.includes('/add/') ||
        path.includes('/change/') ||
        path.includes('/delete/')) {
        return;
    }
    
    console.log('🚀 WebSocket para pedidos iniciado (solo en listado)');
    
    // DETECTAR HTTPS vs HTTP - CORREGIDO
    const isSecure = window.location.protocol === 'https:';
    const wsProtocol = isSecure ? 'wss:' : 'ws:';
    const wsUrl = `${wsProtocol}//${window.location.host}/ws/pedidos/`;
    
    console.log(`🔗 Conectando a: ${wsUrl}`);
    console.log(`🔒 Protocolo seguro: ${isSecure} (${wsProtocol})`);
    
    // Conectar WebSocket con manejo de errores
    let ws;
    
    try {
        ws = new WebSocket(wsUrl);
    } catch (error) {
        console.error('❌ Error creando WebSocket:', error);
        return;
    }

    ws.onopen = () => {
        console.log('✅ WebSocket conectado');
        ws.send(JSON.stringify({ type: 'subscribe' }));
        
        // También pedir pedidos actuales
        setTimeout(() => {
            ws.send(JSON.stringify({ 
                type: 'get_current_pedidos',
                timestamp: new Date().toISOString()
            }));
        }, 1000);
    };

    ws.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            console.log('📨 Mensaje WebSocket recibido:', data.type);
            
            if (data.type === 'pedido_created') {
                console.log(`📦 Nuevo pedido: ${data.pedido.codigo_pedido}`);
                showNotification(data.pedido);
                refreshAdminTable();
            }
            
            if (data.type === 'pedido_updated') {
                console.log(`✏️ Pedido actualizado: ${data.pedido.codigo_pedido}`);
                refreshAdminTable();
            }
            
            if (data.type === 'current_pedidos') {
                console.log(`📊 Pedidos actuales recibidos: ${data.count || 0}`);
                updatePedidoCount(data.count || 0);
            }
            
        } catch (err) {
            console.error('❌ Error procesando mensaje WS:', err);
        }
    };

    ws.onerror = (err) => {
        console.error('❌ WebSocket error:', err);
        // No mostrar alerta al usuario, solo log
    };

    ws.onclose = (event) => {
        console.log(`🔌 WebSocket cerrado: ${event.code} ${event.reason}`);
        
        // Solo reconectar si no fue un cierre normal
        if (event.code !== 1000 && event.code !== 1001) {
            console.log('🔄 Intentando reconexión en 5 segundos...');
            setTimeout(() => {
                location.reload();
            }, 5000);
        }
    };

    function showNotification(pedido) {
        // Usar SweetAlert2 si está disponible
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                toast: true,
                position: 'bottom-end',
                icon: 'success',
                title: '¡Nuevo Pedido!',
                html: `
                    <div style="text-align: left;">
                        <div style="font-weight: bold;">${pedido.codigo_pedido}</div>
                        <div style="font-size: 0.9em; margin-top: 5px;">
                            Cliente: ${pedido.cliente}<br>
                            Yardas: ${pedido.cantidad_yardas}<br>
                            Total: $${pedido.precio_total ? pedido.precio_total.toFixed(2) : '0.00'}
                        </div>
                    </div>
                `,
                showConfirmButton: false,
                timer: 5000,
                timerProgressBar: true,
                background: 'var(--primary)',
                color: 'white',
                customClass: {
                    popup: 'swal-toast'
                },
                didOpen: (toast) => {
                    toast.addEventListener('mouseenter', Swal.stopTimer);
                    toast.addEventListener('mouseleave', Swal.resumeTimer);
                }
            });
        } else {
            // Fallback a notificación nativa
            if (Notification.permission === 'granted') {
                new Notification('Nuevo Pedido', {
                    body: `Pedido ${pedido.codigo_pedido} creado`,
                    icon: '/static/admin/img/icon-alert.svg'
                });
            } else if (Notification.permission !== 'denied') {
                Notification.requestPermission().then(permission => {
                    if (permission === 'granted') {
                        new Notification('Nuevo Pedido', {
                            body: `Pedido ${pedido.codigo_pedido} creado`
                        });
                    }
                });
            }
        }
    }

    function refreshAdminTable() {
        console.log('🔄 Refrescando tabla del admin...');
        
        // Método mejorado: Usar AJAX para refrescar solo la tabla
        const changelist = document.querySelector('#changelist');
        if (!changelist) {
            console.log('⚠️ No se encontró #changelist');
            return;
        }
        
        // Mostrar indicador de carga
        const loadingIndicator = document.createElement('div');
        loadingIndicator.innerHTML = '<div style="text-align: center; padding: 10px; color: var(--primary-600);">🔄 Actualizando...</div>';
        changelist.parentNode.insertBefore(loadingIndicator, changelist);
        
        // Obtener URL actual
        const currentUrl = window.location.href.split('?')[0];
        
        // Hacer petición AJAX
        fetch(currentUrl, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            credentials: 'same-origin'
        })
        .then(response => {
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            return response.text();
        })
        .then(html => {
            // Parsear HTML
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newChangelist = doc.querySelector('#changelist');
            
            if (newChangelist) {
                // Reemplazar contenido
                changelist.innerHTML = newChangelist.innerHTML;
                
                // Agregar animación
                changelist.classList.add('highlight-new');
                setTimeout(() => {
                    changelist.classList.remove('highlight-new');
                }, 2000);
                
                console.log('✅ Tabla refrescada exitosamente');
            }
        })
        .catch(error => {
            console.error('❌ Error refrescando tabla:', error);
            // Fallback suave: solo recargar si es necesario
            if (window.location.search.includes('pedido')) {
                setTimeout(() => {
                    console.log('🔄 Recargando página completa...');
                    window.location.reload();
                }, 3000);
            }
        })
        .finally(() => {
            // Remover indicador de carga
            if (loadingIndicator.parentNode) {
                loadingIndicator.parentNode.removeChild(loadingIndicator);
            }
        });
    }

    function updatePedidoCount(count) {
        // Actualizar contador en la interfaz si existe
        const counterElement = document.querySelector('.pedido-count');
        if (counterElement) {
            counterElement.textContent = `(${count})`;
        }
    }

    // Estilos CSS dinámicos
    const style = document.createElement('style');
    style.textContent = `
        .swal-toast {
            background: var(--primary-700) !important;
            color: white !important;
            border-radius: 8px !important;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        }
        
        .highlight-new {
            animation: highlightPulse 2s ease-in-out;
        }
        
        @keyframes highlightPulse {
            0% { background-color: rgba(var(--primary-rgb, 16, 100, 173), 0.1); }
            50% { background-color: rgba(var(--primary-rgb, 16, 100, 173), 0.3); }
            100% { background-color: transparent; }
        }
        
        .swal-toast .swal2-title {
            color: white !important;
            font-weight: 600 !important;
        }
        
        .swal-toast .swal2-html-container {
            color: rgba(255,255,255,0.9) !important;
        }
    `;
    document.head.appendChild(style);

    // Heartbeat para mantener conexión activa
    let heartbeatInterval;
    
    function startHeartbeat() {
        heartbeatInterval = setInterval(() => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
            }
        }, 30000); // Cada 30 segundos
    }
    
    // Iniciar heartbeat cuando se conecte
    ws.addEventListener('open', startHeartbeat);
    
    // Limpiar al salir
    window.addEventListener('beforeunload', () => {
        if (heartbeatInterval) clearInterval(heartbeatInterval);
        if (ws && ws.readyState === WebSocket.OPEN) {
            ws.close(1000, 'Página cerrada');
        }
    });

    // Verificar si estamos en HTTPS y ajustar WebSocket
    if (isSecure) {
        console.log('🔒 Modo HTTPS detectado, usando WSS');
    } else {
        console.log('⚠️  Modo HTTP detectado, usando WS (menos seguro)');
    }
})();