// store/static/js/admin.js

// Función para actualizar el contador de pedidos pendientes
function updateOrderCounts() {
    console.log('Ejecutando actualización de pedidos...');
    
    // Usar la URL completa con el dominio actual
    const apiUrl = window.location.origin + '/panel/api/order-counts/';
    console.log('Consultando API en:', apiUrl);
    
    fetch(apiUrl)
        .then(response => {
            if (!response.ok) {
                throw new Error('Error en la respuesta del servidor: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos recibidos:', data);
            
            // Actualizar contadores en la UI
            updateElementText('pending-orders-count', data.pending_orders);
            updateElementText('processing-orders-count', data.processing_orders);
            updateElementText('completed-orders-count', data.completed_orders);
            updateElementText('today-orders-count', data.today_orders);
            
            // Actualizar ingresos (con nota de que son solo pedidos completados)
            updateElementText('today-revenue', '$' + data.today_revenue);
            
            // Actualizar badge en el sidebar
            updateSidebarBadge(data.pending_orders);
            
            // Notificar si hay nuevos pedidos
            if (data.new_orders > 0) {
                showNewOrderNotification(data.new_orders);
            }
            
            // Actualizar tabla de pedidos si estamos en la página de pedidos
            if (window.location.pathname.includes('/panel/pedidos/')) {
                refreshOrdersTable();
            }
        })
        .catch(error => {
            console.error('Error al actualizar contadores:', error);
        });
}
// Función auxiliar para actualizar texto de elementos de forma segura
function updateElementText(elementId, text) {
    const element = document.getElementById(elementId);
    if (element) {
        element.textContent = text;
    }
}

// Función para actualizar el badge del sidebar
function updateSidebarBadge(pendingCount) {
    const badge = document.getElementById('sidebar-pending-badge');
    if (badge) {
        if (pendingCount > 0) {
            badge.textContent = pendingCount;
            badge.style.display = 'inline-block';
        } else {
            badge.style.display = 'none';
        }
    }
}

// Función para mostrar notificación de nuevos pedidos
function showNewOrderNotification(count) {
    console.log('Mostrando notificación para', count, 'nuevos pedidos');
    
    // Crear notificación
    const notification = document.createElement('div');
    notification.className = 'alert alert-success alert-dismissible fade show notification-toast';
    notification.innerHTML = `
        <strong>¡Nuevos pedidos!</strong> Tienes ${count} nuevo${count > 1 ? 's' : ''} pedido${count > 1 ? 's' : ''} pendiente${count > 1 ? 's' : ''}.
        <a href="/panel/pedidos/?status=pending" class="alert-link">Ver ahora</a>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Agregar a la página
    document.body.appendChild(notification);
    
    // Reproducir sonido de notificación
    playNotificationSound();
    
    // Remover después de 10 segundos
    setTimeout(() => {
        notification.remove();
    }, 10000);
}

// Función para reproducir sonido de notificación
function playNotificationSound() {
    try {
        console.log('Intentando reproducir sonido de notificación...');
        
        // Usar la URL completa al archivo de sonido
        const audioPath = window.location.origin + '/static/sounds/notification.mp3';
        console.log('Ruta del audio:', audioPath);
        
        const audio = new Audio(audioPath);
        
        // Asegurarse de que el audio se cargue antes de intentar reproducirlo
        audio.addEventListener('canplaythrough', () => {
            console.log('Audio cargado, reproduciendo...');
            const playPromise = audio.play();
            
            if (playPromise !== undefined) {
                playPromise.then(() => {
                    console.log('Audio reproducido con éxito');
                }).catch(error => {
                    console.error('Error al reproducir el audio:', error);
                    
                    // Intentar una reproducción silenciosa si hay problemas de permisos
                    if (error.name === 'NotAllowedError') {
                        console.log('No se permite la reproducción automática. Intentando otra estrategia...');
                        // Podríamos mostrar un botón para que el usuario haga clic y active el sonido
                    }
                });
            }
        });
        
        audio.addEventListener('error', (e) => {
            console.error('Error al cargar el audio:', e);
        });
        
        // Asegurarse de que el audio intente cargarse
        audio.load();
        
    } catch (e) {
        console.error('Error al configurar el audio:', e);
    }
}

// Función para refrescar la tabla de pedidos
function refreshOrdersTable() {
    console.log('Refrescando tabla de pedidos...');
    const ordersTable = document.getElementById('orders-table');
    if (!ordersTable) {
        console.log('Tabla de pedidos no encontrada');
        return;
    }
    
    const currentUrl = window.location.href;
    console.log('Obteniendo tabla actualizada desde:', currentUrl);
    
    fetch(currentUrl)
        .then(response => response.text())
        .then(html => {
            const parser = new DOMParser();
            const doc = parser.parseFromString(html, 'text/html');
            const newTable = doc.getElementById('orders-table');
            
            if (newTable) {
                console.log('Tabla actualizada obtenida, actualizando DOM...');
                ordersTable.innerHTML = newTable.innerHTML;
                
                // Recrear event listeners si es necesario
                setupOrderTableActions();
            } else {
                console.log('No se pudo encontrar el ID de la tabla en el HTML obtenido');
            }
        })
        .catch(error => {
            console.error('Error al actualizar tabla de pedidos:', error);
        });
}

// Configurar event listeners para acciones en la tabla de pedidos
function setupOrderTableActions() {
    // Aquí puedes añadir cualquier inicialización de componentes interactivos
    // como botones de acción, formularios, etc.
}

// Iniciar la actualización periódica cuando la página cargue
document.addEventListener('DOMContentLoaded', () => {
    console.log('Inicializando sistema de actualizaciones en tiempo real...');
    
    // Primera actualización inmediata después de 2 segundos
    setTimeout(() => {
        updateOrderCounts();
    }, 2000);
    
    // Configurar actualización periódica cada 15 segundos
    setInterval(updateOrderCounts, 15000);
    
    // Inicializar event listeners para tablas de pedidos
    setupOrderTableActions();
    
    // Agregar estilos para notificaciones
    const style = document.createElement('style');
    style.textContent = `
        .notification-toast {
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1050;
            width: 350px;
            box-shadow: 0 5px 15px rgba(0,0,0,.15);
        }
    `;
    document.head.appendChild(style);
    
    console.log('Sistema de actualizaciones inicializado correctamente');
});

// Agregar un log simple de inicio
console.log('Admin.js cargado correctamente');