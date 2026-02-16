// static/admin/js/pedidos_websocket_simple.js

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
    
     // DETECTAR HTTPS vs HTTP
    const protocol = window.location.protocol === 'https:' ? 'ws:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/pedidos/`;
    
    console.log(`🔗 Conectando a: ${wsUrl}`);
    
    // Conectar WebSocket
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('✅ WebSocket conectado');
        ws.send(JSON.stringify({ type: 'subscribe' }));
    };

    ws.onmessage = (e) => {
        try {
            const data = JSON.parse(e.data);
            if (data.type === 'pedido_created') {
                console.log(`📦 Nuevo pedido: ${data.pedido.codigo_pedido}`);

                // 1. Mostrar notificación
                showNotification(data.pedido);

                // 2. Refrescar tabla después de 1 segundo
                refreshAdminTable();
                // setTimeout(refreshAdminTable, 1000);
            }
        } catch (err) {
            console.error('Error WS:', err);
        }
    };

    ws.onerror = (err) => console.error('WS error:', err);
    ws.onclose = () => {
        console.log('🔌 WS cerrado, reconectando...');
        setTimeout(() => {
            // Intentar reconectar
            location.reload();
        }, 3000);
    };

    function showNotification(pedido) {
        // Usar SweetAlert2 si está disponible
        if (typeof Swal !== 'undefined') {
            Swal.fire({
                toast: true,
                position: 'bottom-end',
           
              
                html: `
                    <div>
                        <div style="font-weight: bold; margin-bottom: 5px;" >🟠 ¡Nuevo Pedido!</div>
                        <div style="font-size: 14px;">Número de orden: ${pedido.codigo_pedido}</div>
                        <div style="font-size: 14px;">Cliente: ${pedido.cliente}</div>
                        <div style="font-size: 14px;">Detalles: ${pedido.cantidad_yardas} yardas • $${pedido.precio_total ? pedido.precio_total.toFixed(2) : '0.00'}</div>
                    </div>
                `,
                didOpen: () => {
                    
                    // Pausar el temporizador al poner el mouse encima
                    Swal.getPopup().addEventListener('mouseenter', Swal.stopTimer);
                    // Reanudar el temporizador al quitar el mouse
                    Swal.getPopup().addEventListener('mouseleave', Swal.resumeTimer);
                  },
                showConfirmButton: false,
                timer: 3000,
                timerProgressBar: true,
               
        
                customClass: {
                    popup: 'swal-toast'
                }
            });
        }
    }

    function refreshAdminTable() {
        console.log('🔄 Refrescando tabla del admin...');
        // Método 2: Recargar con Fetch
        const changelist = document.querySelector('#changelist');
        if (changelist) {
            fetch(window.location.href)
                .then(r => r.text())
                .then(html => {
                    
                    
                    const temp = document.createElement('div');
                    temp.innerHTML = html;
                    
                    const newChangelist = temp.querySelector('#changelist'); 

                    if (newChangelist) {
                        changelist.innerHTML = newChangelist.innerHTML;
                        console.log('✅ Tabla refrescada');
                    }
                })
                .catch(err => {
                    console.error('Error:', err);
                    // Fallback a recarga completa
                    location.reload();
                });
        } else {
            // Método 3: Recargar página completa como último recurso
            console.log('⚠️ No se pudo refrescar tabla, recargando página...');
            setTimeout(() => location.reload(), 1500);
        }
    }

    // Estilos
    const style = document.createElement('style');
    style.textContent = `
        .dark .swal-toast {
            background:rgb(9, 15, 29) !important;
            color: white;
            
        }

        
        
        .highlight-new {
            animation: highlight 2s ease;
        }
        
        @keyframes highlight {
            0% { background-color: rgba(76, 175, 80, 0.3); }
            100% { background-color: transparent; }
        }
    `;
    document.head.appendChild(style);

    window.addEventListener('beforeunload', () => {
        if (ws.readyState === WebSocket.OPEN) ws.close();
    });
})();