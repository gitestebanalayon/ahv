// static/admin/js/entrega_yardas.js
document.addEventListener('DOMContentLoaded', function() {
    // Función para inicializar validación de yardas
    function initYardasValidation() {
        const yardasInput = document.querySelector('.yardas-input');
        
        if (!yardasInput) return;
        
        const disponibles = parseFloat(yardasInput.dataset.disponibles) || 0;
        const pedidoTotal = parseFloat(yardasInput.dataset.pedidoTotal) || 0;
        
        // Crear o actualizar información de yardas
        let yardasInfo = yardasInput.parentNode.querySelector('.yardas-info');
        if (!yardasInfo) {
            yardasInfo = document.createElement('div');
            yardasInfo.className = 'yardas-info';
            yardasInput.parentNode.appendChild(yardasInfo);
        }
        
        yardasInfo.innerHTML = `
            <strong>Total pedido:</strong> ${pedidoTotal} yardas<br>
            <strong>Disponibles para asignar:</strong> ${disponibles} yardas
        `;
        
        // Validación en tiempo real
        yardasInput.addEventListener('input', function() {
            const valor = parseFloat(this.value) || 0;
            
            if (valor > disponibles) {
                this.style.borderColor = '#dc3545';
                this.style.boxShadow = '0 0 0 0.2rem rgba(220, 53, 69, 0.25)';
            } else {
                this.style.borderColor = '';
                this.style.boxShadow = '';
            }
        });
        
        // Validación al cambiar
        yardasInput.addEventListener('change', function() {
            const valor = parseFloat(this.value) || 0;
            
            if (valor > disponibles) {
                alert(`No puede asignar más de ${disponibles} yardas. Máximo permitido: ${disponibles}`);
                this.value = disponibles;
            }
        });
    }
    
    // Inicializar al cargar
    initYardasValidation();
    
    // También inicializar si se detectan cambios en el DOM
    const observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(mutation) {
            if (mutation.addedNodes.length) {
                initYardasValidation();
            }
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
});