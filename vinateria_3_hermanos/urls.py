"""
URL configuration for vinateria_3_hermanos project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
"""
URL configuration for vinateria_3_hermanos project.
"""
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from tienda import admin_custom

urlpatterns = [
    # Panel de gerencia (ruta no obvia para el admin personalizado)
    path('cp-3h-ops/', admin_custom.admin_site.urls),
    # Autenticación de clientes (allauth)
    path('accounts/', include('allauth.urls')),
    # Rutas públicas de la tienda
    path('', include('tienda.urls', namespace='tienda')),
    # Auth de Django (reset de contraseña, etc.)
    path('', include('django.contrib.auth.urls')),
]

if settings.DEBUG:

    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
