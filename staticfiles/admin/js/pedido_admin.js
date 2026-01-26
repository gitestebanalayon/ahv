// // admin/js/pedido_admin_simple.js

// document.addEventListener('DOMContentLoaded', function() {
//     // Obtener los campos
//     const totalYardasField = document.getElementById('id_cantidad_yardas');
//     const precioYardaField = document.getElementById('id_precio_yarda');
//     const precioTotalField = document.getElementById('id_precio_total');
    
//     // Hacer el campo readonly y cambiar estilo
//     if (precioTotalField) {
//         precioTotalField.readOnly = true;
//         // precioTotalField.style.backgroundColor = '#f8f9fa';
//         precioTotalField.style.color = '#757b81ff';
        
//         // Prevenir cualquier edición manual
//         precioTotalField.addEventListener('keydown', function(e) {
//             if (e.key !== 'Tab' && !e.ctrlKey && !e.metaKey) {
//                 e.preventDefault();
//             }
//         });
        
//         precioTotalField.addEventListener('focus', function() {
//             this.blur(); // Quitar el foco
//         });
//     }
    
//     // Variable para evitar cálculos recursivos
//     let calculando = false;
    
//     // Función para calcular y actualizar precio total
//     function actualizarPrecioTotal() {
//         if (calculando) return;
//         calculando = true;
        
//         const totalYardas = parseFloat(totalYardasField?.value) || 0;
//         const precioYarda = parseFloat(precioYardaField?.value) || 0;
//         const precioTotal = totalYardas * precioYarda;
        
//         if (precioTotalField) {
//             precioTotalField.value = precioTotal.toFixed(2);
            
//             // Forzar a Django a enviar el campo
//             precioTotalField.name = 'precio_total';
//             precioTotalField.setAttribute('name', 'precio_total');
//         }
        
//         calculando = false;
//     }
    
//     // Event listeners para cambios en tiempo real
//     if (totalYardasField) {
//         totalYardasField.addEventListener('input', actualizarPrecioTotal);
//         totalYardasField.addEventListener('change', actualizarPrecioTotal);
//     }
    
//     if (precioYardaField) {
//         precioYardaField.addEventListener('input', actualizarPrecioTotal);
//         precioYardaField.addEventListener('change', actualizarPrecioTotal);
//     }
    
//     // También actualizar cuando la página carga
//     window.addEventListener('load', actualizarPrecioTotal);
//     setTimeout(actualizarPrecioTotal, 500); // Doble seguridad
// });