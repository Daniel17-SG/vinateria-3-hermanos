from django.urls import path
from . import views

app_name = 'tienda'

urlpatterns = [
    # Vistas públicas
    path('', views.index, name='index'),
    path('catalogo/', views.catalogo, name='catalogo'),
    path('catalogo/<str:categoria_slug>/', views.catalogo, name='catalogo_categoria'),
    path('producto/<int:producto_id>/', views.producto_detalle, name='producto_detalle'),
    
    # Autenticación
    path('registro/', views.registro_email, name='registro_email'),
    path('activar/<uidb64>/<token>/', views.activar_cuenta, name='activar_cuenta'),
    path('activacion-enviada/', views.activacion_enviada, name='activacion_enviada'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    
    # Carrito
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('carrito/agregar/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('carrito/actualizar/<int:item_id>/', views.actualizar_carrito, name='actualizar_carrito'),
    path('carrito/eliminar/<int:item_id>/', views.eliminar_carrito, name='eliminar_carrito'),
    path('api/verificar-sesion/', views.verificar_sesion_carrito, name='verificar_sesion'),
    
    # Pago
    path('pago/', views.proceso_pago, name='pago'),
    path('pago/procesar/', views.procesar_pago, name='procesar_pago'),
    path('pago/exitoso/', views.pago_exitoso, name='pago_exitoso'),

    # URLs de PayPal
    path('pago/paypal/crear/', views.crear_orden_paypal, name='crear_orden_paypal'),
    path('pago/paypal/capturar/', views.capturar_orden_paypal, name='capturar_orden_paypal'),
    
    # Administración
    path('admin/productos/', views.admin_productos, name='admin_productos'),
    path('admin/inventario/', views.admin_inventario, name='admin_inventario'),
    path('admin/producto/nuevo/', views.admin_crear_producto, name='admin_crear_producto'),
    path('admin/ventas/', views.admin_ventas, name='admin_ventas'),
    
    # Contacto
    path('api/contacto/', views.contacto, name='contacto'),
    path('api/chatbot/', views.chatbot_responder, name='chatbot_responder'),
    
    # Páginas estáticas
    path('terminos/', views.terminos_condiciones, name='terminos'),
    
    # Perfil de usuario
    path('perfil/', views.mi_perfil, name='mi_perfil'),
    path('perfil/recibo/<int:venta_id>/pdf/', views.descargar_recibo_pdf, name='descargar_recibo_pdf'),
]
