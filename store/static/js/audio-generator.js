// Necesitamos asegurarnos de que existe una carpeta 'sounds' en los estáticos
// Este archivo debería ubicarse en 'store/static/sounds/notification.mp3'
// No podemos incluir directamente archivos de audio en el código, pero podemos
// crear uno programáticamente a través de la API de Web Audio.

// store/static/js/audio-generator.js
// Este script generará un archivo de sonido de notificación

// Ejecutar esto una vez y guardar el archivo MP3 generado en store/static/sounds/notification.mp3

document.addEventListener('DOMContentLoaded', () => {
    // Crear contexto de audio
    const audioContext = new (window.AudioContext || window.webkitAudioContext)();
    
    // Duración del tono en segundos
    const duration = 0.5;
    
    // Crear un buffer para el sonido
    const channels = 1;
    const sampleRate = audioContext.sampleRate;
    const frameCount = sampleRate * duration;
    const buffer = audioContext.createBuffer(channels, frameCount, sampleRate);
    
    // Generar un tono simple
    const data = buffer.getChannelData(0);
    for (let i = 0; i < frameCount; i++) {
        // Una simple onda sinusoidal con frecuencia variable (efecto de "ping")
        const t = i / sampleRate;
        const frequency = 880 * Math.exp(-t * 3); // Frecuencia que disminuye con el tiempo
        data[i] = 0.5 * Math.sin(2 * Math.PI * frequency * t);
        
        // Aplicar una envolvente simple para evitar clics
        const envelope = Math.sin(Math.PI * t / duration);
        data[i] *= envelope;
    }
    
    // Crear un nodo fuente desde el buffer
    const source = audioContext.createBufferSource();
    source.buffer = buffer;
    
    // Conectar al destino (altavoces)
    source.connect(audioContext.destination);
    
    // Reproducir el sonido
    source.start();
    
    // Guardar el sonido como un archivo MP3
    // Nota: esto es una simulación, ya que JavaScript en el navegador no puede guardar
    // archivos directamente en el sistema de archivos del servidor.
    console.log('Por favor, usa una herramienta como Audacity para crear un archivo MP3 de notificación');
});