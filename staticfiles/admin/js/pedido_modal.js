function showPedidoModal(button) {
    // Obtener los datos de los atributos data-*
    const cliente = button.getAttribute('data-cliente');
    const tipoDocumento = button.getAttribute('data-tipo-documento');
    const numero = button.getAttribute('data-numero');
    const fechaEntrega = button.getAttribute('data-fecha-entrega');
    const horaEntrega = button.getAttribute('data-hora-entrega');
    const direccion = button.getAttribute('data-direccion');
    const agregadosTexto = button.getAttribute('data-agregados');
    const agregadosBadges = button.getAttribute('data-agregados-badges');
    const estado = button.getAttribute('data-estado');
    const observacion = button.getAttribute('data-nota');
    const totalYardas = button.getAttribute('data-cantidad-yardas');
    const precioTotal = button.getAttribute('data-precio-total');

    // Crear o seleccionar el modal global
    let modal = document.getElementById('pedido-detalles-modal');
    if (!modal) {
        modal = createModal();
        document.body.appendChild(modal);
    }

    // Rellenar el modal con los datos
    document.getElementById('pedido-modal-cliente').innerText = cliente;
    document.getElementById('pedido-modal-tipo-documento').innerText = tipoDocumento;
    document.getElementById('pedido-modal-numero').innerText = numero;
    document.getElementById('pedido-modal-fecha-entrega').innerText = fechaEntrega;
    document.getElementById('pedido-modal-hora-entrega').innerText = horaEntrega;
    document.getElementById('pedido-modal-direccion').innerText = direccion;
    
    // Mostrar agregados como texto
    // document.getElementById('pedido-modal-agregados-texto').innerText = agregadosTexto || 'Sin agregados';
    
    // Mostrar agregados como badges (si existen)
    const agregadosContainer = document.getElementById('pedido-modal-agregados-badges');
    if (agregadosBadges && agregadosBadges.trim() !== '') {
        agregadosContainer.innerHTML = agregadosBadges;
        agregadosContainer.style.display = 'flex';
    } else {
        agregadosContainer.innerHTML = '';
        agregadosContainer.style.display = 'none';
    }
    
    document.getElementById('pedido-modal-observacion').innerText = observacion || 'Sin observación';
    document.getElementById('pedido-modal-total-yardas').innerText = totalYardas || 'N/A';
    document.getElementById('pedido-modal-precio-total').innerText = precioTotal ? `$${parseFloat(precioTotal).toFixed(2)}` : '$0.00';

    // Actualizar el estado con color correspondiente
    const estadoElement = document.getElementById('pedido-modal-estado');
    estadoElement.innerText = estado;
    
    // Aplicar clase de color según el estado
    estadoElement.className = 'ml-auto inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap ';
    
    switch(estado.toLowerCase()) {
        case 'pendiente':
            estadoElement.className += 'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold badge-warning';
            break;
        case 'programado':
            estadoElement.className += 'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold badge-info';
            break;
        case 'en viaje':
            estadoElement.className += 'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold badge-primary';
            break;
        case 'completado':
            estadoElement.className += 'inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-semibold badge-success';
            break;
        case 'entregado':
            estadoElement.className += 'bg-emerald-100 text-emerald-700 dark:bg-emerald-500/20 dark:text-emerald-400';
            break;
        case 'cancelado':
            estadoElement.className += 'bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400';
            break;
        default:
            estadoElement.className += 'bg-gray-100 text-gray-700 dark:bg-gray-500/20 dark:text-gray-400';
    }

    // Mostrar el modal
    modal.classList.remove('hidden');
    modal.style.display = 'flex';
}

function createModal() {
    const modal = document.createElement('div');
    modal.id = 'pedido-detalles-modal';
    modal.className = 'backdrop-blur-xs bg-base-900/80 flex inset-0 z-50 fixed hx-preserve hidden items-center justify-center';
    modal.innerHTML = `
        <div id="pedido-modal-close" class="absolute inset-0" onclick="closePedidoModal()"></div>

        <div class="bg-white flex m-auto overflow-hidden rounded-default shadow-xs dark:bg-base-800" style="max-width: 600px;">
            <div class="grow h-full overflow-auto relative">
                <div class="flex flex-col h-full">
                    <!-- Contenido principal con scroll normal -->
                    <div class="flex flex-col grow overflow-auto p-3">
                        <div class="flex flex-col gap-4">
                            <div>
                                <h3 class="grid grid-cols-2 mb-3">
                                    <div class="flex items-center font-semibold text-font-important-light dark:text-font-important-dark">
                                        <span class="material-symbols-outlined mr-2">info</span>
                                        Más detalles
                                    </div>
                                    <div id="pedido-modal-estado" class="ml-auto inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap">
                                        <!-- El estado se llenará dinámicamente -->
                                    </div>
                                </h3>
                                <div class="flex flex-col rounded-default shadow-xs dark:border-base-700">
                                    <div class="grid grid-cols-2 gap-4">
                                        <div>
                                            <div class="border dark:border-base-700 group flex flex-col overflow-hidden rounded-default transition-all bg-white-100 dark:bg-base-800">
                                                <span class="flex items-center justify-center grow font-semibold p-2">
                                                    <span class="material-symbols-outlined align-middle text-sm mr-2" style="font-size: 24px;">assignment_ind</span>
                                                    Datos del cliente
                                                </span>
                                                <div class="block border-t border-base-200 px-6 py-4 dark:border-base-700" style="height: 92px; overflow-y: auto;">
                                                    <p><strong>Nombre:</strong> <span id="pedido-modal-cliente"></span></p>
                                                    <p><strong>Tipo Documento:</strong> <span id="pedido-modal-tipo-documento"></span></p>
                                                    <p><strong>Número:</strong> <span id="pedido-modal-numero"></span></p>
                                                </div>
                                            </div>
                                        </div>
                                        <div>
                                            <div class="border dark:border-base-700 group flex flex-col overflow-hidden rounded-default transition-all bg-white-100 dark:bg-base-800">
                                                <span class="flex items-center justify-center grow font-semibold p-2">
                                                    <span class="material-symbols-outlined align-middle text-sm mr-2" style="font-size: 24px;">assignment_ind</span>
                                                    Datos de entrega
                                                </span>
                                                <div class="block border-t border-base-200 px-6 py-4 dark:border-base-700" style="height: 92px; overflow-y: auto;">
                                                    <p><strong>Fecha entrega:</strong> <span id="pedido-modal-fecha-entrega"></span></p>
                                                    <p><strong>Hora entrega:</strong> <span id="pedido-modal-hora-entrega"></span></p>
                                                    <p><strong>Dirección entrega:</strong> <span id="pedido-modal-direccion"></span></p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="mt-4">
                                        <div class="border dark:border-base-700 group flex flex-col overflow-hidden rounded-default transition-all bg-white-100 dark:bg-base-800">
                                            <div class="block px-6 py-4 dark:border-base-800">
                                                <p class="mt-1">
                                                    <strong>Agregados:</strong>
                                                    
                                                </p>
                                                <div id="pedido-modal-agregados-badges" class="mt-2 flex flex-wrap gap-1" style="display: none;">
                                                    <!-- Los badges se insertarán dinámicamente aquí -->
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="bg-white-100 mt-4 border dark:border-base-700 px-6 py-4 rounded-default dark:bg-base-800" style="height: 92px; overflow-y: auto;">
                                        <p><strong>Observación:</strong> <span id="pedido-modal-observacion"></span></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Pie del modal -->
                    <div class="bg-white flex flex-col gap-2 p-3 pt-1 dark:bg-base-800">
                        <div class="border border-base-200 grid grid-cols-3 gap-4 p-4 rounded bg-gray-50 dark:bg-base-800 dark:border-base-700">
                            <div>
                                <p><strong>Total Yardas:</strong> <span id="pedido-modal-total-yardas"></span></p>
                            </div>
                            <div></div>
                            <div>
                                <p><strong>Precio Total:</strong> <span id="pedido-modal-precio-total"></span></p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    return modal;
}



function closePedidoModal() {
    const modal = document.getElementById('pedido-detalles-modal');
    if (modal) {
        modal.classList.add('hidden');
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Cerrar modal al hacer clic fuera del contenido
document.addEventListener('DOMContentLoaded', function() {
    // Delegación de eventos para el área de cierre
    document.addEventListener('click', function(event) {
        const modal = document.getElementById('pedido-detalles-modal');
        if (modal && !modal.classList.contains('hidden') && event.target.id === 'pedido-modal-close') {
            closePedidoModal();
        }
    });
    
    // También cerrar el modal al presionar ESC
    document.addEventListener('keydown', function(event) {
        const modal = document.getElementById('pedido-detalles-modal');
        if (event.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
            closePedidoModal();
        }
    });
});

