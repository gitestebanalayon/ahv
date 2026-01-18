document.addEventListener('DOMContentLoaded', function () {
    const conductorField = document.querySelector('#id_conductor');
    const vehiculoSelect = document.querySelector('#id_vehiculo');

    if (conductorField && vehiculoSelect) {
        const vehiculoLabel = document.querySelector('label[for="id_vehiculo"]');
        if (vehiculoLabel) {
            // Verificar si ya tiene el texto automático
            if (!vehiculoLabel.textContent.includes('Campo automático')) {
                vehiculoLabel.innerHTML += ' <span style="color:#28a745; font-size:0.9em; font-weight:bold;">Campo automático</span>';
            }
        }

        // Crear un campo oculto que mantenga el valor real
        const hiddenInput = document.createElement('input');
        hiddenInput.type = 'hidden';
        hiddenInput.name = vehiculoSelect.name; // Mismo name para mantener compatibilidad
        hiddenInput.id = 'vehiculo_hidden';
        hiddenInput.value = vehiculoSelect.value || '';

        // Reemplazar el name del select para que no interfiera
        vehiculoSelect.name = 'vehiculo_display_only';

        // Estilizar el select como visualización
        vehiculoSelect.disabled = true; // IMPORTANTE: no deshabilitar

        // vehiculoSelect.className = `
        //     border border-base-200 bg-white font-medium min-w-20 placeholder-base-400 
        //     rounded-default shadow-xs text-font-default-light text-sm focus:outline-2 
        //     focus:-outline-offset-2 focus:outline-primary-600 group-[.errors]:border-red-600 
        //     focus:group-[.errors]:outline-red-600 dark:bg-base-900 dark:border-base-700 
        //     dark:text-font-default-dark dark:group-[.errors]:border-red-500 
        //     dark:focus:group-[.errors]:outline-red-500 dark:scheme-dark group-[.primary]:border-transparent 
        //     disabled:!bg-base-50 dark:disabled:!bg-base-800 px-3 py-2 w-full pr-8! max-w-2xl appearance-none truncate 
        // `;

        vehiculoSelect.style.cssText = `
            cursor: not-allowed;
            pointer-events: none;
            user-select: none;
        `;


        // Insertar el campo oculto
        vehiculoSelect.parentNode.insertBefore(hiddenInput, vehiculoSelect);

        // Función para actualizar ambos campos
        function updateVehiculoField(vehiculoId, vehiculoText = '') {
            hiddenInput.value = vehiculoId || '';

            if (vehiculoId) {
                // Buscar o crear opción en el select de visualización
                let optionExists = false;
                for (let option of vehiculoSelect.options) {
                    if (option.value == vehiculoId) {
                        vehiculoSelect.value = vehiculoId;
                        optionExists = true;
                        break;
                    }
                }

                if (!optionExists && vehiculoId) {
                    const newOption = document.createElement('option');
                    newOption.value = vehiculoId;
                    newOption.text = vehiculoText || `Vehículo ID: ${vehiculoId}`;
                    vehiculoSelect.appendChild(newOption);
                    vehiculoSelect.value = vehiculoId;
                }
            } else {
                vehiculoSelect.value = '';
            }
        }

        conductorField.addEventListener('change', function () {
            const conductorId = this.value;

            if (conductorId) {
                fetch(`/conductor/listar?conductor_id=${conductorId}`)
                    .then(response => response.json())
                    .then(data => {
                        if (data.data?.length > 0) {
                            const vehiculoId = data.data[0].vehiculo_id?.id;
                            updateVehiculoField(vehiculoId);
                        }
                    });
            } else {
                updateVehiculoField('');
            }
        });

        // Inicializar
        if (conductorField.value) {
            conductorField.dispatchEvent(new Event('change'));
        }
    }


});

document.addEventListener('DOMContentLoaded', async function () {
    const yardasAsignadasField = document.querySelector('#id_yardas_asignadas');
    const urlParams = new URLSearchParams(window.location.search);
    let pedido_id = Number(urlParams.get('pedido') || urlParams.get('pedido_id'));

    // Variables globales
    let cantidadTotalPedido = 0; // cantidad_yardas del pedido
    let yardasYaAsignadas = 0;   // Suma de yardas_asignadas de todas las entregas
    let entregaActualId = null;  // ID de la entrega actual si estamos editando
    let codigo_entrega = null;

    // Obtener datos completos del pedido
    async function obtenerDatosPedido(idPedido) {
        try {
            const response = await fetch(`/pedido/listar?pedido_id=${idPedido}`);

            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }

            const data = await response.json();

            if (!data.data || data.data.length === 0) {
                throw new Error('No se encontraron datos del pedido');
            }

            const pedido = data.data[0];
            
            // Obtener cantidad total del pedido
            cantidadTotalPedido = parseFloat(pedido.cantidad_yardas) || 0;
            
           
            // Obtener entregas existentes
            if (pedido.entregas && pedido.entregas.length > 0) {
                // Obtener ID de la entrega actual (si estamos editando)
                
                entregaActualId = obtenerIdEntregaActual();

                if (entregaActualId != null) {
                           const entrega_data = pedido.entregas.find(item => item.id === entregaActualId);
                codigo_entrega = entrega_data.codigo_entrega;
                }
                
                // Calcular yardas ya asignadas (excluyendo la entrega actual si estamos editando)
                yardasYaAsignadas = pedido.entregas.reduce((total, entrega) => {
                    // Si estamos editando una entrega, excluirla del cálculo
                    if (entregaActualId && entrega.id == entregaActualId) {
                        return total;
                    }
                    return total + (parseFloat(entrega.yardas_asignadas) || 0);
                }, 0);
            }

            
            
            

            // console.log('📊 Datos del pedido obtenidos:', {
            //     cantidadTotalPedido: cantidadTotalPedido,
            //     yardasYaAsignadas: yardasYaAsignadas,
            //     entregasExistentes: pedido.entregas?.length || 0,
            //     entregaActualExcluida: entregaActualId
            // });

            return true;
        } catch (error) {
            console.error('❌ Error al obtener datos del pedido:', error);
            throw error;
        }
    }

    // Función para obtener ID de entrega actual (si estamos editando)
    function obtenerIdEntregaActual() {
        // Verificar si estamos en una página de edición
        if (window.location.pathname.includes('/change/')) {
            const match = window.location.pathname.match(/\/entrega\/(\d+)\/change\//);
            if (match) return parseInt(match[1]);
        }
        
        // Buscar campo ID oculto
        const idField = document.querySelector('#id_id, input[name="id"]');
        if (idField && idField.value) {
            return parseInt(idField.value);
        }
        
        return null;
    }

    // Calcular yardas disponibles
    function calcularYardasDisponibles() {
        return Math.max(0, cantidadTotalPedido - yardasYaAsignadas);
    }

    // Mostrar información de yardas
    function mostrarInformacionYardas(valorIngresado) {
        let displayContainer = document.querySelector('#yardas-display-container');

        if (!displayContainer) {
            // Crear contenedor si no existe
            displayContainer = document.createElement('div');
            displayContainer.id = 'yardas-display-container';
            displayContainer.style.cssText = `
                margin-top: 20px;
                padding: 12px;
               
            `;

             displayContainer.className = `
                border border-base-200 rounded-default dark:border-base-700
            `;

            

            // Insertar después del campo
            yardasAsignadasField.parentNode.insertBefore(displayContainer, yardasAsignadasField.nextSibling);
        }

        // Convertir valor ingresado
        const valorIngresadoNum = parseFloat(valorIngresado.replace(',', '.')) || 0;
        
        // Calcular total proyectado
        const totalProyectado = yardasYaAsignadas + valorIngresadoNum;
        const yardasDisponibles = calcularYardasDisponibles();
        
        // Determinar si excede el límite
        const excedeLimite = totalProyectado > cantidadTotalPedido;
        const porcentaje = cantidadTotalPedido > 0 ? (totalProyectado / cantidadTotalPedido) * 100 : 0;

        // Generar HTML
        displayContainer.innerHTML = `
            <div class="block font-semibold mb-2 text-font-important-light text-sm dark:text-font-important-dark">
                📊 Control de Yardas
            </div>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 12px;">
                <div style="text-align: center;">
                    <div style=" margin-bottom: 3px;">Total Pedido</div>
                    <div style="font-weight: 700;">${cantidadTotalPedido.toFixed(1)}</div>
                </div>
                <div style="text-align: center;">
                    <div style=" margin-bottom: 3px;">Ya Asignadas</div>
                    <div style="font-weight: 700; ">${yardasYaAsignadas.toFixed(1)}</div>
                </div>
                <div style="text-align: center;">
                    <div style=" margin-bottom: 3px;">Disponibles</div>
                    <div style="font-weight: 700; color: #17a2b8;">${yardasDisponibles.toFixed(1)}</div>
                </div>
            </div>
            
            <div style="margin-bottom: 10px;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span>Progreso: ${porcentaje.toFixed(1)}%</span>
                    <span>${totalProyectado.toFixed(1)} / ${cantidadTotalPedido.toFixed(1)} yardas</span>
                </div>
                <div style="height: 8px; background: #e9ecef; border-radius: 4px; overflow: hidden;">
                    <div style="height: 100%; width: ${Math.min(100, porcentaje)}%; 
                          background: ${excedeLimite ? '#dc3545' : '#28a745'};">
                    </div>
                </div>
            </div>
            
            <div style=" padding: 8px; border-radius: 6px; 
                  background: ${excedeLimite ? '#f8d7da' : '#d4edda'}; 
                  color: ${excedeLimite ? '#721c24' : '#155724'};
                  border: 1px solid ${excedeLimite ? '#f5c6cb' : '#c3e6cb'};">
                ${excedeLimite 
                    ? `⚠ <strong>Excede límite:</strong> Has sobrepasado por ${(totalProyectado - cantidadTotalPedido).toFixed(1)} yardas` 
                    : `✓ <strong>Dentro del límite:</strong> Quedan ${(cantidadTotalPedido - totalProyectado).toFixed(1)} yardas disponibles`
                }
            </div>
            
            ${entregaActualId ? 
                `<div style="margin-top: 8px; text-align: center;">
                    Editando entrega: #${codigo_entrega}
                </div>` 
                : ''
            }
        `;

        // Cambiar estilo del input si excede
      
    }

    // Inicializar
    try {
        // Obtener datos del pedido
        await obtenerDatosPedido(pedido_id);

        if (yardasAsignadasField) {
            const valorInicial = yardasAsignadasField.value || '0';
            
            // console.log('Valor inicial del campo:', valorInicial);
            // console.log('Cantidad total del pedido:', cantidadTotalPedido);
            // console.log('Yardas ya asignadas en otras entregas:', yardasYaAsignadas);
            // console.log('Yardas disponibles:', calcularYardasDisponibles());
            // console.log('Editando entrega ID:', entregaActualId || 'Nueva entrega');

            // Mostrar información inicial
            mostrarInformacionYardas(valorInicial);

            // Validar y mostrar cambios en tiempo real
            yardasAsignadasField.addEventListener('input', function () {
                const valorTiempoReal = this.value;
                console.log('Valor cambiado:', valorTiempoReal);
                mostrarInformacionYardas(valorTiempoReal);
            });

            // Validar al perder foco
            yardasAsignadasField.addEventListener('blur', function () {
                const valor = parseFloat(this.value.replace(',', '.')) || 0;
                const totalProyectado = yardasYaAsignadas + valor;
                
                if (totalProyectado > cantidadTotalPedido) {
                    const maxPermitido = cantidadTotalPedido - yardasYaAsignadas;
                    
                 
                    this.value = maxPermitido.toFixed(1).replace('.', ',');
                    mostrarInformacionYardas(this.value);
                }
            });

            // Prevenir que se escriban valores inválidos
            yardasAsignadasField.addEventListener('keypress', function (e) {
                const char = String.fromCharCode(e.keyCode || e.which);
                const currentValue = this.value;
                
                // Solo permitir números, punto, coma y teclas de control
                if (!/[\d\.,]|Backspace|Delete|Arrow/.test(e.key) && 
                    !e.ctrlKey && !e.metaKey) {
                    e.preventDefault();
                }
                
                // Si es punto o coma, verificar que no haya ya uno
                if ((char === '.' || char === ',') && (currentValue.includes('.') || currentValue.includes(','))) {
                    e.preventDefault();
                }
            });
        }
    } catch (error) {
        console.error('Error al inicializar:', error);
        
        // Mostrar mensaje de error
        if (yardasAsignadasField) {
            const errorContainer = document.createElement('div');
            errorContainer.style.cssText = `
                margin-top: 10px;
                padding: 10px;
                background: #f8d7da;
                border: 1px solid #f5c6cb;
                border-radius: 6px;
                color: #721c24;
                font-size: 14px;
            `;
            errorContainer.textContent = 'Error al cargar los datos del pedido';
            yardasAsignadasField.parentNode.insertBefore(errorContainer, yardasAsignadasField.nextSibling);
        }
    }
});



// Método con debounce (para evitar muchos logs)
// let timeoutId;
// yardasAsignadasField.addEventListener('input', function() {
//     clearTimeout(timeoutId);
//     timeoutId = setTimeout(() => {

//         const valorEstablecido = this.value;

//     }, 500);
// });