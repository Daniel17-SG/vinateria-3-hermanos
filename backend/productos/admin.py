from django.contrib import admin
from .models import Producto # Importamos tu modelo

admin.site.register(Producto) # Esto hace la magia
