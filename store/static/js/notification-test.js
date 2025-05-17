// store/static/js/notification-test.js

// Este archivo es solo para pruebas, se debe cargar manualmente en el HTML
// para verificar que el sistema de notificaciones esté funcionando

document.addEventListener('DOMContentLoaded', () => {
    console.log('Notification test script loaded');
    
    // Crear botón de prueba
    const testButton = document.createElement('button');
    testButton.className = 'btn btn-warning position-fixed';
    testButton.style.bottom = '20px';
    testButton.style.right = '20px';
    testButton.style.zIndex = '1050';
    testButton.innerHTML = 'Probar Notificación';
    
    // Agregar al DOM
    document.body.appendChild(testButton);
    
    // Agregar evento de clic
    testButton.addEventListener('click', () => {
        console.log('Test button clicked');
        
        // Probar reproducción de audio
        testAudio();
        
        // Mostrar notificación de prueba
        const notification = document.createElement('div');
        notification.className = 'alert alert-success alert-dismissible fade show notification-toast';
        notification.innerHTML = `
            <strong>¡Prueba de notificación!</strong> Esto es una prueba del sistema de notificaciones.
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        `;
        document.body.appendChild(notification);
        
        // Remover después de 5 segundos
        setTimeout(() => {
            notification.remove();
        }, 5000);
    });
    
    // Función para probar reproducción de audio
    function testAudio() {
        console.log('Testing audio...');
        
        // Intentar cargar el audio desde varias rutas posibles
        const audioPaths = [
            '/static/sounds/notification.mp3',
            '/staticfiles/sounds/notification.mp3',
            window.location.origin + '/static/sounds/notification.mp3',
            '/media/sounds/notification.mp3',
            './static/sounds/notification.mp3',
            '../static/sounds/notification.mp3'
        ];
        
        // Intentar reproducir audio con cada ruta
        audioPaths.forEach(path => {
            console.log('Trying audio path:', path);
            const audio = new Audio(path);
            
            audio.addEventListener('canplaythrough', () => {
                console.log('Audio loaded successfully from:', path);
                audio.play()
                    .then(() => console.log('Audio played successfully from:', path))
                    .catch(e => console.error('Error playing audio from:', path, e));
            });
            
            audio.addEventListener('error', () => {
                console.error('Failed to load audio from:', path);
            });
            
            // Comenzar a cargar
            audio.load();
        });
        
        // También probar reproducción inmediata (podría fallar por políticas del navegador)
        try {
            const directAudio = new Audio('/static/sounds/notification.mp3');
            directAudio.play()
                .then(() => console.log('Direct audio play succeeded'))
                .catch(e => console.error('Direct audio play failed:', e));
        } catch (e) {
            console.error('Error setting up direct audio:', e);
        }
    }
});