import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vinateria_3_hermanos.settings')
django.setup()

User = get_user_model()
# Datos para tu superusuario
username = 'admin'
email = 'admin@example.com'
password = '123'  # Pon una contraseña real aquí

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f"Superusuario '{username}' creado exitosamente.")
else:
    print(f"El superusuario '{username}' ya existe.")
