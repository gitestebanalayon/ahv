function showPedidoModal(button) {
    // Obtener los datos de los atributos data-*
    const cliente = button.getAttribute('data-cliente');
    const tipoDocumento = button.getAttribute('data-tipo-documento');
    const numero = button.getAttribute('data-numero');
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
    let modal = document.getElementById('changelist-filter');
    if (!modal) {
        // Crear el modal si no existe
        modal = createModal();
        document.body.appendChild(modal);
    }
    

    // Rellenar el modal con los datos
    document.getElementById('pedido-modal-cliente').innerText = cliente;
    document.getElementById('pedido-modal-tipo-documento').innerText = tipoDocumento;
    document.getElementById('pedido-modal-numero').innerText = numero;
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


    // Mostrar el modal - remover clase hidden y ajustar display
    modal.classList.remove('hidden');
    modal.style.display = 'flex'; // O el valor correcto para tu layout
}

function createModal() {
    const modal = document.createElement('div');
    modal.id = 'changelist-filter';
    modal.className = 'backdrop-blur-xs bg-base-900/80 flex inset-0 z-50 fixed hx-preserve hidden items-center justify-center';
    modal.innerHTML = `
           <div id="changelist-filter-close" class="absolute inset-0" x-on:click="filterOpen = false"></div>

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
                                            Mas detalles
                                        </div>
                                        <div class="ml-auto inline-block font-semibold h-6 leading-6 px-2 rounded-default text-[11px] uppercase whitespace-nowrap bg-red-100 text-red-700 dark:bg-red-500/20 dark:text-red-400">
                                            <span id="pedido-modal-estado"></span>
                                        </div>
                                    </h3>
                                    <div class="flex flex-col rounded-default shadow-xs dark:border-base-700">
                                        <div class="grid grid-cols-2 gap-4">
                                            <div>
                                                <div class="border dark:border-base-700 group flex flex-col overflow-hidden rounded-default transition-all bg-white-100  dark:bg-base-800 ">
                                                    <span class="flex items-center justify-center grow font-semibold p-2">
                                                        <span class="material-symbols-outlined align-middle text-sm mr-2" style="font-size: 24px;">assignment_ind</span>
                                                        Datos del cliente
                                                    </span>

                                                    <div class="block border-t border-base-200 px-6 py-4 dark:border-base-700">
                                                        <p class=""><strong>Usuario:</strong> <span id="pedido-modal-cliente"></span></p>
                                                        <p class=""><strong>Tipo Documento:</strong> <span id="pedido-modal-tipo-documento"></span></p>
                                                        <p class=""><strong>Número:</strong> <span id="pedido-modal-numero"></span></p>
                                                    </div>
                                                </div>
                                            </div>
                                            <div>
                                                <div class="border dark:border-base-700 group flex flex-col overflow-hidden rounded-default transition-all bg-white-100  dark:bg-base-800 ">
                                                    <span class="flex items-center justify-center grow font-semibold p-2">
                                                        <span class="material-symbols-outlined align-middle text-sm mr-2" style="font-size: 24px;">assignment_ind</span>
                                                        Datos de entrega
                                                    </span>

                                                    <div class="block border-t border-base-200 px-6 py-4 dark:border-base-700" style="height: 92px; overflow-y: auto;">
                                                        <p class=""><strong>Fecha entrega:</strong> <span id="pedido-modal-fecha-entrega"></span></p>
                                                        <p class=""><strong>Hora entrega:</strong> <span id="pedido-modal-hora-entrega"></span></p>
                                                        <p class=""><strong>Dirección entrega:</strong> <span id="pedido-modal-direccion"></span></p>
                                                    </div>
                                                </div>
                                            </div>

                                            <div>
                                                <div class="border dark:border-base-700 group flex flex-col overflow-hidden rounded-default transition-all bg-white-100  dark:bg-base-800 ">
                                                    

                                                    <div class=" block px-6 py-4 dark:border-base-800">
                                                        <p class=""><strong>Conductor:</strong> <span id="pedido-modal-conductor"></span>
                                                </p>
                                                    </div>
                                                </div>
                                            </div>

                                            <div>
                                                <div class="border dark:border-base-700 group flex flex-col overflow-hidden rounded-default transition-all bg-white-100  dark:bg-base-800 ">
                                                   

                                                    <div class="text-green-100 block px-6 py-4 dark:border-base-800">
                                                            <p class=""><strong>Vehículo:</strong> <span id="pedido-modal-vehiculo"></span></p>
                                                </p>
                                                </p>
                                                    </div>
                                                </div>
                                            </div>

                                            
                                        </div>
                                        <div class="bg-white-100 mt-4 border dark:border-base-700 px-6 py-4 rounded-default dark:bg-base-800" style="height: 92px; overflow-y: auto;">
                                                <p class=""><strong>Observación:</strong> <span
                                                        id="pedido-modal-observacion"></span></p>
                                            </div>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <!-- Pie del modal -->
                        <div
                            class="bg-white flex flex-col gap-2 p-3 pt-1 dark:bg-base-800">
                            <div
                                class="border border-base-200 grid grid-cols-3 gap-4 p-4 rounded bg-gray-50 dark:bg-base-800 dark:border-base-700">
                                <div>
                                    <p class=""><strong>Total Yardas:</strong> <span id="pedido-modal-total-yardas"></span></p>
                                </div>
                                <div>
                                    <p class=""><strong>Precio por Yarda:</strong> <span id="pedido-modal-precio-yarda"></span></p>
                                </div>
                                <div>
                                    <p class=""><strong>Precio Total:</strong> <span id="pedido-modal-precio-total"></span></p>
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
    console.log("Cerrando modal");
    const modal = document.getElementById('changelist-filter');
    if (modal) {
        
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
        // También podrías agregar modal.style.display = 'none' si es necesario
    }
}

// Cerrar modal al hacer clic fuera del contenido
document.addEventListener('DOMContentLoaded', function() {
    // Delegación de eventos para el área de cierre
    document.addEventListener('click', function(event) {
        const modal = document.getElementById('changelist-filter');
        if (modal && !modal.classList.contains('hidden') && event.target.id === 'changelist-filter-close') {
            closePedidoModal();
        }
    });
    
    // También podrías cerrar el modal al presionar ESC
    document.addEventListener('keydown', function(event) {
        const modal = document.getElementById('changelist-filter');
        if (event.key === 'Escape' && modal && !modal.classList.contains('hidden')) {
            closePedidoModal();
        }
    });
});


{/* <div id="changelist-filter" class="backdrop-blur-xs bg-base-900/80 flex inset-0 z-50 fixed " hx-preserve="" x-show="filterOpen" style="display: none;">
    <div id="changelist-filter-close" class="grow " x-on:click="filterOpen = false"></div>

    <div class="bg-white flex m-4 overflow-hidden rounded-default shadow-xs w-80 dark:bg-base-800 ">
        <div class="grow h-full overflow-auto relative ">
            <div class="flex flex-col h-full ">
                <div class="flex flex-col grow gap-4 overflow-auto *:mb-0" data-simplebar="init" data-simplebar-direction="rtl">
                    <div class="simplebar-wrapper" style="margin: 0px;">
                        <div class="simplebar-height-auto-observer-wrapper">
                            <div class="simplebar-height-auto-observer">

                            </div>
                        </div>
                        <div class="simplebar-mask">
                            <div class="simplebar-offset" style="right: 0px; bottom: 0px;">
                                <div class="simplebar-content-wrapper" tabindex="0" role="region" aria-label="scrollable content" style="height: auto; overflow: hidden;">
                                    <div class="simplebar-content" style="padding: 0px;">
                                        <div class="flex flex-col gap-4 px-3 py-2.5  *:mb-0">
                                            <div>
                                                <h3 class="font-semibold mb-2 text-font-important-light dark:text-font-important-dark">
                                                    By country 
                                                </h3>
                                                <ul class="border border-base-200 flex flex-col rounded-default shadow-xs dark:border-base-700">  
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 font-semibold text-primary-600 dark:text-primary-500 ">
                                                        <a href="?" title="All" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            All
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=70th+Anniversary" title="70th Anniversary" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            70th Anniversary
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Abu+Dhabi" title="Abu Dhabi" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Abu Dhabi
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Australia" title="Australia" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Australia
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Austria" title="Austria" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Austria
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Azerbaijan" title="Azerbaijan" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Azerbaijan
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Bahrain" title="Bahrain" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Bahrain
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Belgium" title="Belgium" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Belgium
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Brazil" title="Brazil" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Brazil
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Canada" title="Canada" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Canada
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=China" title="China" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            China
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Eifel" title="Eifel" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Eifel
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Emilia+Romagna" title="Emilia Romagna" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Emilia Romagna
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Europe" title="Europe" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Europe
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=France" title="France" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            France
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Germany" title="Germany" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Germany
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Great+Britain" title="Great Britain" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Great Britain
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Hungary" title="Hungary" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Hungary
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Italy" title="Italy" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Italy
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Japan" title="Japan" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Japan
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Malaysia" title="Malaysia" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Malaysia
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Mexico" title="Mexico" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Mexico
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Monaco" title="Monaco" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Monaco
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Netherlands" title="Netherlands" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Netherlands
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Portugal" title="Portugal" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Portugal
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Qatar" title="Qatar" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Qatar
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Russia" title="Russia" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Russia
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Sakhir" title="Sakhir" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Sakhir
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Saudi+Arabia" title="Saudi Arabia" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Saudi Arabia
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Singapore" title="Singapore" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Singapore
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Spain" title="Spain" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Spain
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Styria" title="Styria" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Styria
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Turkey" title="Turkey" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Turkey
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=Tuscany" title="Tuscany" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            Tuscany
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=United+Arab+Emirates" title="United Arab Emirates" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            United Arab Emirates
                                                        </a>
                                                    </li>
                                                
                                                    <li class="border-b border-base-200 last:border-b-0 dark:border-base-700 hover:text-base-700 dark:hover:text-base-200">
                                                        <a href="?country=United+States" title="United States" class="block px-3 py-2 hover:text-primary-600 dark:hover:text-primary-500">
                                                            United States
                                                        </a>
                                                    </li>
                                                </ul>    
                                            </div>   
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="simplebar-placeholder" style="width: 0px; height: 0px;">
                        </div>
                    </div>
                    <div class="simplebar-track simplebar-horizontal" style="visibility: hidden;">
                        <div class="simplebar-scrollbar" style="width: 0px; display: none;">
                        </div>
                    </div>
                    <div class="simplebar-track simplebar-vertical" style="visibility: hidden;">
                        <div class="simplebar-scrollbar" style="height: 0px; display: none; transform: translate3d(0px, 0px, 0px);">
                        </div>
                    </div>
                </div>
                <div class="bg-white border-t border-base-200 flex flex-col gap-2 p-3 py-2.5 dark:bg-base-800 dark:border-base-700">
                    <span id="changelist-filter-extra-actions" class="flex flex-row gap-2 items-center">
                        <a href="?_facets=True" class="viewlink border border-base-200 grow font-medium px-3 py-2 rounded-default text-center transition-all w-full lg:w-auto dark:border-base-700 dark:hover:text-base-200">
                            Show counts
                        </a>
                    </span>
                </div>
            </div>
        </div>
    </div>
</div> */}



// // Función para mostrar el modal con los datos del pedido
// function showPedidoModal(button) {
//     // Obtener los datos de los atributos data-*
//     const id = button.getAttribute('data-id');
//     const cliente = button.getAttribute('data-cliente');
//     const conductor = button.getAttribute('data-conductor');
//     const vehiculo = button.getAttribute('data-vehiculo');
//     const fechaEntrega = button.getAttribute('data-fecha-entrega');
//     const horaEntrega = button.getAttribute('data-hora-entrega');
//     const direccion = button.getAttribute('data-direccion');
//     const estado = button.getAttribute('data-estado');
//     const observacion = button.getAttribute('data-observacion');
//     const totalYardas = button.getAttribute('data-total-yardas');
//     const precioYarda = button.getAttribute('data-precio-yarda');
//     const precioTotal = button.getAttribute('data-precio-total');

//     // Crear o seleccionar el modal global
//     let modal = document.getElementById('pedido-modal-global');
//     if (!modal) {
//         // Crear el modal si no existe
//         modal = createModal();
//         document.body.appendChild(modal);
//     }

//     // Rellenar el modal con los datos
//     document.getElementById('pedido-modal-title').innerText = `Pedido #${id}`;
//     document.getElementById('pedido-modal-cliente').innerText = cliente;
//     document.getElementById('pedido-modal-conductor').innerText = conductor;
//     document.getElementById('pedido-modal-vehiculo').innerText = vehiculo;
//     document.getElementById('pedido-modal-fecha-entrega').innerText = fechaEntrega;
//     document.getElementById('pedido-modal-hora-entrega').innerText = horaEntrega;
//     document.getElementById('pedido-modal-direccion').innerText = direccion;
//     document.getElementById('pedido-modal-estado').innerText = estado;
//     document.getElementById('pedido-modal-observacion').innerText = observacion || 'Sin observación';
//     document.getElementById('pedido-modal-total-yardas').innerText = totalYardas || 'N/A';
//     document.getElementById('pedido-modal-precio-yarda').innerText = precioYarda ? `$${parseFloat(precioYarda).toFixed(2)}` : 'N/A';
//     document.getElementById('pedido-modal-precio-total').innerText = precioTotal ? `$${parseFloat(precioTotal).toFixed(2)}` : 'N/A';

   
//     // Mostrar el modal
//     modal.classList.remove('hidden');
// }

// // Función para crear el modal (solo una vez)
// function createModal() {
//     const modal = document.createElement('div');
//     modal.id = 'pedido-modal-global';
//     modal.className = 'hidden fixed inset-0 z-50 overflow-y-auto';
//     modal.innerHTML = `
//         <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
//             <div class="fixed inset-0 transition-opacity" aria-hidden="true">
//                 <div class="absolute inset-0 bg-gray-500 opacity-75"></div>
//             </div>
//             <span class="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
//             <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-lg sm:w-full">
//                 <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
//                     <div class="sm:flex sm:items-start">
//                         <div class="mt-3 text-center sm:mt-0 sm:ml-4 sm:text-left w-full">
//                             <h3 class="text-lg leading-6 font-medium text-gray-900" id="pedido-modal-title">
//                                 Pedido #
//                             </h3>
//                             <div class="mt-4">
//                                 <div class="grid grid-cols-2 gap-4">
//                                     <div>
//                                         <p class="text-gray-500"><strong>Cliente:</strong> <span id="pedido-modal-cliente"></span></p>
//                                         <p class="text-gray-500"><strong>Conductor:</strong> <span id="pedido-modal-conductor"></span></p>
//                                         <p class="text-gray-500"><strong>Vehículo:</strong> <span id="pedido-modal-vehiculo"></span></p>
//                                     </div>
//                                     <div>
//                                         <p class="text-gray-500"><strong>Fecha entrega:</strong> <span id="pedido-modal-fecha-entrega"></span></p>
//                                         <p class="text-gray-500"><strong>Hora entrega:</strong> <span id="pedido-modal-hora-entrega"></span></p>
//                                         <p class="text-gray-500"><strong>Estado:</strong> <span id="pedido-modal-estado"></span></p>
//                                     </div>
//                                 </div>
//                                 <div class="mt-4">
//                                     <p class="text-gray-500"><strong>Dirección:</strong> <span id="pedido-modal-direccion"></span></p>
//                                     <p class="text-gray-500"><strong>Observación:</strong> <span id="pedido-modal-observacion"></span></p>
//                                 </div>
//                                 <div class="mt-4 grid grid-cols-3 gap-4 bg-gray-50 p-4 rounded">
//                                     <div>
//                                         <p class="text-gray-500"><strong>Total Yardas:</strong> <span id="pedido-modal-total-yardas"></span></p>
//                                     </div>
//                                     <div>
//                                         <p class="text-gray-500"><strong>Precio por Yarda:</strong> <span id="pedido-modal-precio-yarda"></span></p>
//                                     </div>
//                                     <div>
//                                         <p class="text-gray-500"><strong>Precio Total:</strong> <span id="pedido-modal-precio-total"></span></p>
//                                     </div>
//                                 </div>
//                             </div>
//                         </div>
//                     </div>
//                 </div>
//                 <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">

//                     <button type="button" onclick="closePedidoModal()" class="mt-3 w-full inline-flex justify-center rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 sm:mt-0 sm:ml-3 sm:w-auto sm:text-sm">
//                         Cerrar
//                     </button>
//                 </div>
//             </div>
//         </div>
//     `;
//     return modal;
// }

// // Función para cerrar el modal
// function closePedidoModal() {
//     console.log("Cerrando modal");

//     const modal = document.getElementById('pedido-modal-global');
//     if (modal) {
//         modal.classList.add('hidden');
//         document.body.style.overflow = 'auto'; // Restaurar scroll
//     }
// }

// // Cerrar modal al hacer clic fuera del contenido
// document.addEventListener('DOMContentLoaded', function() {
//     document.addEventListener('click', function(event) {
//         const modal = document.getElementById('pedido-modal-global');
//         if (modal && !modal.classList.contains('hidden') && event.target === modal) {
//             closePedidoModal();
//         }
//     });
// });

