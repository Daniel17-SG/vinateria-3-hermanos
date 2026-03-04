================================================================================
 README TÉCNICO - VINATERÍA 3 HERMANOS
================================================================================

SISTEMA E-COMMERCE CON DJANGO - V 1.0

================================================================================
 1. MÓDULOS DEL SISTEMA Y SUS FUNCIONES
================================================================================

1.1 MÓDULO DE AUTENTICACIÓN (django-allauth)
----------------------------------------------
- Registro de usuarios con email y contraseña
- Login/Logout
- Autenticación social con Google OAuth 2.0
- Recuperación de contraseña (password_reset)
- Perfil de cliente asociado a cada usuario

1.2 MÓDULO DE CATÁLOGO
------------------------
- Listado de productos con paginación (8 por página)
- Búsqueda por nombre y descripción (Q objects)
- Filtro por categorías (Tequila, Whisky, Brandy, Vodka, Ron)
- Productos relacionados en detalle de producto
- Optimización N+1 con select_related('categoria')

1.3 MÓDULO DE CARRITO DE COMPRAS
----------------------------------
- Agregar/Actualizar/Eliminar productos
- Persistencia de sesión por usuario autenticado
- Cálculo automático de subtotales
- Validación de stock en tiempo real

1.4 MÓDULO DE PAGOS (PayPal REST API)
---------------------------------------
- Creación de órdenes PayPal
- Captura de pagos
- Manejo de errores (cancelación, fallido)
- Redirección a página de éxito
- Validación de propiedad de venta

1.5 MÓDULO DE PERFIL DE USUARIO
---------------------------------
- Visualización de datos del cliente
- Historial de pedidos con paginación (10 por página)
- Modal de detalles de cada orden
- Descarga de recibos en PDF (xhtml2pdf)

1.6 MÓDULO DE ADMINISTRACIÓN (Django Admin)
---------------------------------------------
- Panel de control con Dashboard
- KPIs: Ventas Hoy/Semana/Mes, Ingresos Totales
- Gráficos: Ventas diarias (Chart.js), Categorías más vendidas
- Alertas visuales de stock bajo (<10) y agotado
- Exportación a Excel (.xlsx)
- Filtros por rango de fechas
- Acciones masivas para actualizar estatus

1.7 MÓDULO DE CONTACTO
------------------------
- Formulario en footer
- Validación de datos
- Almacenamiento en BD
- Notificaciones toast

1.8 MÓDULO DE GOOGLE MAPS
---------------------------
- Mapa interactivo en footer
- Marcador personalizado
- InfoWindow con información
- Estilos personalizados (oscuro)

================================================================================
 2. LO QUE FALTA DESARROLLAR O MEJORAR
================================================================================

2.1 SEGURIDAD
--------------
[ ] Implementar django-axes para prevenir ataques de fuerza bruta
[ ] Agregar HTTPS forzado en producción
[ ] Implementar rate limiting en APIs
[ ] Añadir logs de auditoría (django-simple-history)

2.2 FUNCIONALIDADES E-COMMERCE
-------------------------------
[ ] Sistema de comentarios y valoraciones de productos
[ ] Lista de deseos (wishlist)
[ ] Cupones de descuento
[ ] Políticas de devolución
[ ] Chat de atención al cliente (widget)

2.3 PAGO
--------
[ ] Integrar Stripe como pasarela alternativa
[ ] Notificaciones por email al completar compra
[ ] Facturación automática (CFDI para México)

2.4 RENDIMIENTO
----------------
[ ] Implementar cache con Redis
[ ] Optimización de imágenes (django-imagekit)
[ ] Carga diferida de imágenes (lazy loading)
[ ] CDN para archivos estáticos

2.5 ADMINISTRACIÓN
-------------------
[ ] Panel de analytics avanzado
[ ] Reportes en PDF con ReportLab
[ ] dashboard con más métricas
[ ] Gestión de usuarios desde el frontend

2.6 FRONTEND
-------------
[ ] Página de términos y condiciones completa
[ ] Página de política de privacidad
[ ] FAQ (Preguntas frecuentes)
[ ] Blog/Noticias

2.7 DEPLOYMENT
---------------
[ ] Configuración para producción (gunicorn, nginx)
[ ] Dockerfile y docker-compose.yml
[ ] CI/CD con GitHub Actions
[ ] Configuración en Google Cloud Platform

================================================================================
 3. CÓMO INICIAR EL SISTEMA
================================================================================

3.1 REQUISITOS PREVIOS
-----------------------
- Python 3.9 o superior
- Git
- Navegador web moderno

3.2 CLONAR Y CONFIGURAR
-------------------------
# Clonar repositorio
git clone <URL_DEL_REPOSITORIO>
cd vinateria-3-hermanos

# Crear entorno virtual
python -m venv venv

# Activar (Windows)
venv\Scripts\activate

# Activar (Linux/Mac)
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

3.3 CONFIGURAR VARIABLES DE ENTORNO
------------------------------------
# Copiar archivo de ejemplo (si trabajas en desarrollo local)
# cp .env.example .env
#
# Configuración de variables de entorno:
# - En producción no almacenes valores sensibles en archivos de texto dentro del repositorio.
# - Usa el gestor de secretos de la plataforma (Render, AWS Secrets Manager, GitHub Secrets, .etc.)
# - Define las variables necesarias desde la UI de secretos de tu plataforma de despliegue.
#
# Variables requeridas (ejemplos):
# - clave secreta de Django (configurar en el gestor de secretos)
# - flag DEBUG (usar False en producción)
# - hosts permitidos (ALLOWED_HOSTS, coma-separado)
# - credenciales de OAuth (cliente/secret de proveedore x), API keys externas
# - credenciales de pasarela de pago y modo (sandbox/live)

3.4 PREPARAR BASE DE DATOS
---------------------------
# Crear migraciones (si hay cambios en modelos)
python manage.py makemigrations

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic

3.5 INICIAR SERVIDOR
---------------------
python manage.py runserver

El servidor estará disponible en: http://127.0.0.1:8000

3.6 ACCESOS
-----------
- Panel Admin: http://127.0.0.1:8000/cp-3h-ops/
- Dashboard: http://127.0.0.1:8000/cp-3h-ops/
- Catálogo: http://127.0.0.1:8000/catalogo/

================================================================================
 4. ESTRUCTURA DE DIRECTORIOS
================================================================================

vinateria-3-hermanos/
├── vinateria_3_hermanos/    # Configuración del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── tienda/                  # App principal
│   ├── admin.py            # Configuración del admin
│   ├── admin_custom.py     # Admin personalizado con dashboard
│   ├── models.py           # Modelos de base de datos
│   ├── views.py            # Vistas de la aplicación
│   ├── urls.py             # Rutas de la app
│   ├── context_processors.py
│   └── migrations/
├── templates/              # Plantillas HTML
│   └── tienda/
├── static/                 # Archivos estáticos
│   └── tienda/
├── media/                  # Imágenes de productos
├── templates/admin/        # Plantillas del admin
└── db.sqlite3             # Base de datos

================================================================================
 5. VARIABLES DE ENTORNO REQUERIDAS (resumen)
================================================================================

Este proyecto requiere variables de entorno para funcionar correctamente. Por
seguridad, NUNCA almacenes valores sensibles en archivos de texto dentro del
repositorio. En producción, utiliza el gestor de secretos de la plataforma de
despliegue (por ejemplo Render, GitHub Secrets, AWS Secrets Manager, etc.).

Las variables incluyen claves secretas, credenciales de servicios externos
y flags de configuración (DEBUG, ALLOWED_HOSTS, credenciales de PayPal/Google,
API keys). Define estos valores desde la UI de secretos de tu plataforma de
despliegue o mediante un vault; no los pongas en archivos de texto en el repo.

================================================================================
 6. TECNOLOGÍAS UTILIZADAS
================================================================================

Backend:
- Django 6.0
- Python 3.9+
- SQLite3

Autenticación:
- django-allauth
- Google OAuth 2.0

Pagos:
- PayPal REST API
- xhtml2pdf (PDF)

Admin:
- django-admin-sortable2
- Chart.js
- openpyxl (Excel)

Frontend:
- HTML5/CSS3
- JavaScript (Vanilla)
- Font Awesome

================================================================================
 7. CONTACTO Y SOPORTE
================================================================================

Desarrollado para: Vinatería Los 3 Hermanos
Versión: 1.0
Fecha: Febrero 2026

Para dudas técnicas, revisar la documentación de Django:
https://docs.djangoproject.com/

================================================================================
