// Función para mostrar el modal con los datos del pedido
function showPedidoModal(button) {
    // Obtener los datos de los atributos data-*
    const id = button.getAttribute('data-id');
    const cliente = button.getAttribute('data-cliente');
    const conductor = button.getAttribute('data-conductor');
    const vehiculo = button.getAttribute('data-vehiculo');
    const fechaEntrega = button.getAttribute('data-fecha-entrega');
    const horaEntrega = button.getAttribute('data-hora-entrega');
    const direccion = button.getAttribute('data-direccion');
    const estado = button.getAttribute('data-estado');
    const observacion = button.getAttribute('data-observacion');
    const totalYardas = button.getAttribute('data-total-yardas');
    const precioYarda = button.getAttribute('data-precio-yarda');
    const precioTotal = button.getAttribute('data-precio-total');

    // Crear o seleccionar el modal global
    let modal = document.getElementById('pedido-modal-global');
    if (!modal) {
        // Crear el modal si no existe
        modal = createModal();
        document.body.appendChild(modal);
    }

    // Rellenar el modal con los datos
    document.getElementById('pedido-modal-title').innerText = `Pedido #${id}`;
    document.getElementById('pedido-modal-cliente').innerText = cliente;
    document.getElementById('pedido-modal-conductor').innerText = conductor;
    document.getElementById('pedido-modal-vehiculo').innerText = vehiculo;
    document.getElementById('pedido-modal-fecha-entrega').innerText = fechaEntrega;
    document.getElementById('pedido-modal-hora-entrega').innerText = horaEntrega;
    document.getElementById('pedido-modal-direccion').innerText = direccion;
    document.getElementById('pedido-modal-estado').innerText = estado;
    document.getElementById('pedido-modal-observacion').innerText = observacion || 'Sin observación';
    document.getElementById('pedido-modal-total-yardas').innerText = totalYardas || 'N/A';
    document.getElementById('pedido-modal-precio-yarda').innerText = precioYarda ? `$${parseFloat(precioYarda).toFixed(2)}` : 'N/A';
    document.getElementById('pedido-modal-precio-total').innerText = precioTotal ? `$${parseFloat(precioTotal).toFixed(2)}` : 'N/A';

    // Actualizar el enlace de editar
    const editLink = document.getElementById('pedido-modal-edit-link');
    editLink.href = `/admin/sistema/pedido/${id}/change/`;

    // Mostrar el modal
    modal.classList.remove('hidden');
}

// Función para crear el modal (solo una vez)
function createModal() {
    const modal = document.createElement('div');
    modal.id = 'pedido-modal-global';
    modal.className = 'hidden fixed inset-0 z-50 overflow-y-auto';
    modal.innerHTML = `
        <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
            <div class="fixed inset-0 transition-opacity" aria-hidden="true">
                <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
            </div>
            <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
            <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
                <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
                    <div class="sm:flex sm:items-start">
                        <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
                            <h3 class="text-lg leading-6 font-medium text-gray-900" id="pedido-modal-title">
                                Pedido #
                            </h3>
                            <div class="mt-4">
                                <div class="grid grid-cols-2 gap-4">
                                    <div>
                                        <p class="text-gray-500"><strong>Cliente:</strong> <span id="pedido-modal-cliente"></span></p>
                                        <p class="text-gray-500"><strong>Conductor:</strong> <span id="pedido-modal-conductor"></span></p>
                                        <p class="text-gray-500"><strong>Vehículo:</strong> <span id="pedido-modal-vehiculo"></span></p>
                                    </div>
                                    <div>
                                        <p class="text-gray-500"><strong>Fecha entrega:</strong> <span id="pedido-modal-fecha-entrega"></span></p>
                                        <p class="text-gray-500"><strong>Hora entrega:</strong> <span id="pedido-modal-hora-entrega"></span></p>
                                        <p class="text-gray-500"><strong>Estado:</strong> <span id="pedido-modal-estado"></span></p>
                                    </div>
                                </div>
                                <div class="mt-4">
                                    <p class="text-gray-500"><strong>Dirección:</strong> <span id="pedido-modal-direccion"></span></p>
                                    <p class="text-gray-500"><strong>Observación:</strong> <span id="pedido-modal-observacion"></span></p>
                                </div>
                                <div class="mt-4 grid grid-cols-3 gap-4 bg-gray-50 p-4 rounded">
                                    <div>
                                        <p class="text-gray-500"><strong>Total Yardas:</strong> <span id="pedido-modal-total-yardas"></span></p>
                                    </div>
                                    <div>
                                        <p class="text-gray-500"><strong>Precio por Yarda:</strong> <span id="pedido-modal-precio-yarda"></span></p>
                                    </div>
                                    <div>
                                        <p class="text-gray-500"><strong>Precio Total:</strong> <span id="pedido-modal-precio-total"></span></p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
                    <a id="pedido-modal-edit-link" href="#" class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm">
                        Editar
                    </a>
                    <button type="button" onclick="closePedidoModal()" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
                        Cerrar
                    </button>
                </div>
            </div>
        </div>
    `;
    return modal;
}

// Función para cerrar el modal
function closePedidoModal() {
    const modal = document.getElementById('pedido-modal-global');
    if (modal) {
        modal.classList.add('hidden');
    }
}

// Cerrar modal al hacer clic fuera del contenido
document.addEventListener('DOMContentLoaded', function() {
    document.addEventListener('click', function(event) {
        const modal = document.getElementById('pedido-modal-global');
        if (modal && !modal.classList.contains('hidden') && event.target === modal) {
            closePedidoModal();
        }
    });
});