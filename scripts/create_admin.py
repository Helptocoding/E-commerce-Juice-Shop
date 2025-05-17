#!/usr/bin/env python
# scripts/create_admin.py

import os
import sys
import django

# Mostrar mensaje de inicio
print("Iniciando script para crear usuario administrador...")

# Configurar el entorno Django
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'juice_shop.settings')
django.setup()

print("Entorno Django configurado correctamente.")

from django.contrib.auth.models import User
from django.db.utils import IntegrityError

def create_admin_user(username='admin', email='admin@example.com', password='admin123'):
    """
    Crea un superusuario con los datos proporcionados.
    """
    try:
        print(f"Intentando crear superusuario '{username}'...")
        
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=email,
                password=password
            )
            print(f"✅ Superusuario '{username}' creado exitosamente.")
        else:
            print(f"⚠️ El usuario '{username}' ya existe.")
    except IntegrityError as e:
        print(f"❌ Error al crear el superusuario: {e}")
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

if __name__ == '__main__':
    print("Procesando argumentos...")
    # Si se proporcionan argumentos, los usamos como credenciales
    if len(sys.argv) >= 4:
        print(f"Usando credenciales personalizadas: usuario='{sys.argv[1]}'")
        create_admin_user(
            username=sys.argv[1],
            email=sys.argv[2],
            password=sys.argv[3]
        )
    else:
        # De lo contrario, usamos valores predeterminados
        print("Usando credenciales por defecto: usuario='admin'")
        create_admin_user()
    
    print("Script finalizado.")