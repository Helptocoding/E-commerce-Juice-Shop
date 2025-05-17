#!/usr/bin/env python
# scripts/check_sounds.py

import os
import sys
from pathlib import Path

# Configurar el entorno Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juice_shop.settings')

import django
django.setup()

from django.conf import settings

def check_sound_file():
    """
    Comprueba si el archivo de sonido de notificación existe y es accesible.
    """
    print("Verificando configuración de archivos estáticos...\n")
    
    # Verificar configuración de STATIC_ROOT y STATICFILES_DIRS
    print(f"STATIC_URL: {settings.STATIC_URL}")
    print(f"STATIC_ROOT: {settings.STATIC_ROOT}")
    print(f"STATICFILES_DIRS: {settings.STATICFILES_DIRS}")
    print()
    
    # Verificar si existe la carpeta de sonidos en cada ubicación posible
    possible_sound_dirs = [
        Path(settings.STATIC_ROOT) / 'sounds',
        *[Path(d) / 'sounds' for d in settings.STATICFILES_DIRS],
    ]
    
    print("Buscando carpeta 'sounds':")
    for sound_dir in possible_sound_dirs:
        exists = sound_dir.exists()
        status = "✅ EXISTE" if exists else "❌ NO EXISTE"
        print(f" - {sound_dir}: {status}")
        
        if exists:
            # Verificar si el archivo notification.mp3 existe
            sound_file = sound_dir / 'notification.mp3'
            file_exists = sound_file.exists()
            file_status = "✅ EXISTE" if file_exists else "❌ NO EXISTE"
            print(f"   - {sound_file}: {file_status}")
            
            if file_exists:
                # Verificar permisos
                try:
                    with open(sound_file, 'rb') as f:
                        size = len(f.read())
                    print(f"   - Tamaño: {size} bytes")
                    print(f"   - Permisos: ✅ LEGIBLE")
                except Exception as e:
                    print(f"   - Permisos: ❌ ERROR: {str(e)}")
    
    print("\nVerificando estructura del proyecto:")
    
    # Verificar la estructura actual del proyecto
    project_dir = Path(settings.BASE_DIR)
    static_dir = project_dir / 'static'
    
    if static_dir.exists():
        print(f" - {static_dir}: ✅ EXISTE")
        sounds_dir = static_dir / 'sounds'
        
        if not sounds_dir.exists():
            print(f" - {sounds_dir}: ❌ NO EXISTE")
            print("\n¡ACCIÓN REQUERIDA! Crear directorio:")
            print(f"  mkdir -p {sounds_dir}")
    else:
        print(f" - {static_dir}: ❌ NO EXISTE")
        print("\n¡ACCIÓN REQUERIDA! Crear directorio:")
        print(f"  mkdir -p {static_dir}/sounds")
    
    # Verificar si necesitamos crear el archivo de sonido
    notification_file = static_dir / 'sounds' / 'notification.mp3'
    if not notification_file.exists():
        print(f" - {notification_file}: ❌ NO EXISTE")
        print("\n¡ACCIÓN REQUERIDA! Necesitas crear o descargar un archivo de audio MP3")
        print("y colocarlo en la ruta correcta. Puedes usar un sonido de notificación simple.")
        print(f"El archivo debe llamarse 'notification.mp3' y debe ubicarse en '{static_dir}/sounds/'")
    
    print("\nRecuerda ejecutar el siguiente comando después de crear los archivos:")
    print("python manage.py collectstatic --noinput")
    
    return True

if __name__ == '__main__':
    success = check_sound_file()
    if success:
        print("\nVerificación completada. Consulta las acciones requeridas, si las hay.")
    else:
        print("\nError durante la verificación.")