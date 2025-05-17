// store/static/js/cart.js

document.addEventListener('DOMContentLoaded', function() {
    console.log('Script del carrito cargado correctamente');
    
    // Prevenir el envío normal de todos los formularios de "Agregar al carrito"
    // Usamos una selección más amplia para asegurarnos de capturar todos los formularios
    const addToCartForms = document.querySelectorAll('.add-to-cart-form');
    console.log('Formularios de agregar al carrito encontrados:', addToCartForms.length);
    
    addToCartForms.forEach(form => {
        console.log('Configurando interceptor para formulario:', form);
        
        // Marcar el formulario para diagnóstico
        form.setAttribute('data-cart-js-attached', 'true');
        
        form.addEventListener('submit', function(e) {
            // Detener el comportamiento normal del formulario
            e.preventDefault();
            console.log('Interceptando envío de formulario para producto');
            
            const formData = new FormData(form);
            const submitButton = form.querySelector('button[type="submit"]');
            
            // Desactivar el botón para evitar múltiples envíos
            if (submitButton) submitButton.disabled = true;
            
            // Añadir un token CSRF si no está ya incluido
            if (!formData.get('csrfmiddlewaretoken')) {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                formData.append('csrfmiddlewaretoken', csrfToken);
            }
            
            // Enviar petición AJAX
            fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': formData.get('csrfmiddlewaretoken')
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                console.log('Respuesta del servidor:', data);
                
                if (data.success) {
                    // Actualizar contador de carrito en el navbar
                    updateCartBadge(data.cart_count);
                    
                    // Mostrar notificación
                    showAddedToCartNotification(data.product_name || 'Producto', data.quantity || 1);
                    
                    // Reactivar el botón
                    if (submitButton) submitButton.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error al agregar producto al carrito:', error);
                
                // Reactivar el botón en caso de error
                if (submitButton) submitButton.disabled = false;
                
                // Mostrar notificación de error
                showErrorNotification('No se pudo agregar el producto al carrito');
            });
        });
    });
    
    // Función para actualizar el badge del carrito
    function updateCartBadge(count) {
        const cartBadges = document.querySelectorAll('.fa-shopping-cart + .badge');
        const cartCountText = document.querySelector('.cart-dropdown-header .text-muted');
        
        // Actualizar todos los badges
        cartBadges.forEach(badge => {
            badge.textContent = count;
            badge.style.display = count > 0 ? 'inline-block' : 'none';
        });
        
        // Actualizar el contador en el dropdown
        if (cartCountText) {
            cartCountText.textContent = `${count} item${count !== 1 ? 's' : ''}`;
        }
    }
    
    // Función para mostrar notificación de producto agregado
    function showAddedToCartNotification(productName, quantity) {
        // Eliminar notificaciones anteriores
        const oldNotifications = document.querySelectorAll('.product-added-notification');
        oldNotifications.forEach(notification => notification.remove());
        
        // Crear nueva notificación
        const notification = document.createElement('div');
        notification.className = 'product-added-notification';
        notification.innerHTML = `
            <i class="fas fa-check-circle"></i>
            <span>${quantity}x ${productName} agregado al carrito</span>
        `;
        
        // Agregar al DOM
        document.body.appendChild(notification);
        
        // Eliminar después de 3 segundos
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    // Función para mostrar notificación de error
    function showErrorNotification(message) {
        // Eliminar notificaciones anteriores
        const oldNotifications = document.querySelectorAll('.error-notification');
        oldNotifications.forEach(notification => notification.remove());
        
        // Crear nueva notificación
        const notification = document.createElement('div');
        notification.className = 'error-notification';
        notification.innerHTML = `
            <i class="fas fa-exclamation-circle"></i>
            <span>${message}</span>
        `;
        
        // Agregar al DOM
        document.body.appendChild(notification);
        
        // Eliminar después de 3 segundos
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }
    
    // Evitar que al hacer click en formularios del dropdown se cierre
    document.querySelectorAll('.cart-dropdown form').forEach(form => {
        form.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    });
    
    // Publicar variable global para diagnóstico
    window.addToCartForms = addToCartForms;
    
    console.log('Inicialización del carrito completada');
});