document.addEventListener('DOMContentLoaded', function () {
    const conductorField = document.querySelector('#id_conductor');
    const vehiculoSelect = document.querySelector('#id_vehiculo');

    if (conductorField && vehiculoSelect) {
        // Quitar el texto "Campo automático" del label
        const vehiculoLabel = document.querySelector('label[for="id_vehiculo"]');
        if (vehiculoLabel) {
            // Eliminar cualquier indicador de campo automático
            vehiculoLabel.innerHTML = vehiculoLabel.innerHTML.replace(/<span[^>]*>Campo automático<\/span>/, '');
        }

        // QUITAR TODA LA LÓGICA DE CAMPO AUTOMÁTICO
        
        // Restaurar el select a su estado normal (quitar cualquier deshabilitación)
        vehiculoSelect.disabled = false;
        
        // Quitar estilos de solo lectura visual
        vehiculoSelect.style.cssText = '';
        
        // Restaurar el nombre original si fue cambiado
        if (vehiculoSelect.name === 'vehiculo_display_only') {
            vehiculoSelect.name = 'vehiculo';
        }
        
        // Eliminar el campo oculto si existe
        const hiddenInput = document.querySelector('#vehiculo_hidden');
        if (hiddenInput) {
            hiddenInput.remove();
        }
        
        // Remover cualquier evento de cambio en el conductor que modifique el vehículo
        // Guardar referencia al evento original
        const originalOnChange = conductorField.onchange;
        
        // Reemplazar el evento change con uno que no afecte el vehículo
        conductorField.addEventListener('change', function() {
            // Aquí puedes agregar lógica si necesitas, pero NO modifica el vehículo
            const conductorId = this.value;
            // console.log('Conductor seleccionado:', conductorId);
            // El vehículo permanece sin cambios
        });
        
        // Opcional: Mantener cualquier otra lógica del conductor si es necesario
        if (originalOnChange) {
            conductorField.addEventListener('change', originalOnChange);
        }

        // Cargar vehículos al inicio si es necesario
        // console.log('✅ Sistema de selección libre activado');
        // console.log('👉 Conductor y vehículo ahora son campos independientes');
    }
});

// EL RESTO DEL CÓDIGO SOBRE YARDAS SE MANTIENE EXACTAMENTE IGUAL

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
                // console.log('Valor cambiado:', valorTiempoReal);
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