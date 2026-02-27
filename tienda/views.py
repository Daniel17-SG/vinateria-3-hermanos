from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache  # <-- NUEVO IMPORT PARA EL CACHÉ
from django.db import transaction, IntegrityError, DatabaseError
from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit
import requests
import json

from .models import Categoria, Producto, CarritoItem, Venta, DetalleVenta, PerfilCliente, MensajeContacto


# ==================== VISTAS PÚBLICAS ====================

def index(request):
    """Página principal - productos destacados"""
    productos_destacados = Producto.objects.filter(activo=True, stock__gt=0)[:4]
    categorias = Categoria.objects.filter(activo=True)
    
    context = {
        'productos_destacados': productos_destacados,
        'categorias': categorias,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY, 
    }
    return render(request, 'tienda/index.html', context)


def catalogo(request):
    """Catálogo de productos con búsqueda y filtros por categoría"""
    categoria_slug = request.GET.get('categoria')
    query = request.GET.get('q', '').strip()
    
    productos = Producto.objects.filter(activo=True, stock__gt=0)
    categorias = Categoria.objects.filter(activo=True)
    
    if query:
        productos = productos.filter(
            Q(nombre__icontains=query) | Q(descripcion__icontains=query)
        )
    
    if categoria_slug:
        productos = productos.filter(categoria__slug=categoria_slug)
    
    productos = productos.select_related('categoria')
    
    paginator = Paginator(productos, 8)
    page_number = request.GET.get('page')
    productos_page = paginator.get_page(page_number)
    
    context = {
        'productos': productos_page,
        'categorias': categorias,
        'categoria_actual': categoria_slug,
        'busqueda_actual': query,
    }
    return render(request, 'tienda/catalogo.html', context)


def producto_detalle(request, producto_id):
    """Página de detalle de un producto"""
    producto = get_object_or_404(Producto, id=producto_id, activo=True)
    relacionados = Producto.objects.filter(
        categoria=producto.categoria, 
        activo=True
    ).exclude(id=producto.id)[:4]
    
    context = {
        'producto': producto,
        'productos_relacionados': relacionados,
    }
    return render(request, 'tienda/producto_detalle.html', context)


# ==================== AUTENTICACIÓN ====================

@ratelimit(key='ip', rate='10/m', method='POST', block=True)
def registro(request):
    """Registro de nuevos usuarios"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            PerfilCliente.objects.create(user=user)
            login(request, user)
            messages.success(request, '¡Bienvenido! Tu cuenta ha sido creada.')
            return redirect('tienda:index')
        else:
            messages.error(request, 'Por favor corrige los errores below.')
    else:
        form = UserCreationForm()
    
    return render(request, 'tienda/registro.html', {'form': form})


@ratelimit(key='ip', rate='5/m', method='POST', block=True)
def login_view(request):
    """Inicio de sesión"""
    if request.user.is_authenticated:
        return redirect('tienda:index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'tienda:index')
                messages.success(request, f'¡Bienvenido de nuevo, {username}!')
                return redirect(next_url)
        messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'tienda/login.html', {'form': form})


@never_cache
def logout_view(request):
    """Cerrar sesión y limpiar caché del navegador para evitar el botón 'Atrás'"""
    logout(request) # Destruye la sesión en el servidor
    messages.info(request, 'Has cerrado sesión correctamente.')
    
    # Preparamos la redirección asegurando el namespace
    response = redirect('tienda:index')
    
    # Inyectamos cabeceras para forzar al navegador a olvidar las páginas anteriores
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    
    return response


# ==================== CARRITO DE COMPRAS ====================

@login_required
def ver_carrito(request):
    """Ver carrito de compras"""
    items = CarritoItem.objects.select_related('producto').filter(usuario=request.user)
    total = sum(item.subtotal for item in items)
    
    context = {
        'items': items,
        'total': total,
    }
    return render(request, 'tienda/carrito.html', context)


@login_required
@require_POST
def agregar_carrito(request, producto_id):
    """Agregar producto al carrito - con protección contra race conditions"""
    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad <= 0:
        return JsonResponse({'success': False, 'error': 'Cantidad inválida'})
    
    try:
        with transaction.atomic():
            producto = Producto.objects.select_for_update().filter(
                id=producto_id, 
                activo=True,
                stock__gte=cantidad
            ).first()
            
            if not producto:
                return JsonResponse({'success': False, 'error': 'Stock insuficiente'})
            
            item, created = CarritoItem.objects.get_or_create(
                usuario=request.user,
                producto=producto,
                defaults={'cantidad': cantidad}
            )
            
            if not created:
                nueva_cantidad = item.cantidad + cantidad
                if nueva_cantidad > producto.stock:
                    return JsonResponse({'success': False, 'error': 'Stock insuficiente'})
                item.cantidad = nueva_cantidad
                item.save()
        
        carrito_count = CarritoItem.objects.filter(usuario=request.user).count()
        
        return JsonResponse({
            'success': True, 
            'carrito_count': carrito_count,
            'message': f'{producto.nombre} agregado al carrito'
        })
        
    except (DatabaseError, IntegrityError):
        return JsonResponse({'success': False, 'error': 'Error de base de datos'}, status=500)


@login_required
@require_POST
def actualizar_carrito(request, item_id):
    """Actualizar cantidad de un item"""
    item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    cantidad = int(request.POST.get('cantidad', 1))
    
    if cantidad <= 0:
        item.delete()
        message = 'Producto eliminado del carrito'
    elif cantidad <= item.producto.stock:
        item.cantidad = cantidad
        item.save()
        message = 'Cantidad actualizada'
    else:
        return JsonResponse({'success': False, 'error': 'Stock insuficiente'})
    
    # Recalcular total
    items = CarritoItem.objects.select_related('producto').filter(usuario=request.user)
    total = sum(i.subtotal for i in items)
    
    return JsonResponse({
        'success': True,
        'nueva_cantidad': item.cantidad if cantidad > 0 else 0,
        'subtotal': float(item.subtotal) if cantidad > 0 else 0,
        'total': float(total),
        'message': message
    })


@login_required
@require_POST
def eliminar_carrito(request, item_id):
    """Eliminar item del carrito"""
    item = get_object_or_404(CarritoItem, id=item_id, usuario=request.user)
    item.delete()
    
    # Recalcular total
    items = CarritoItem.objects.select_related('producto').filter(usuario=request.user)
    total = sum(i.subtotal for i in items)
    count = items.count()
    
    return JsonResponse({
        'success': True,
        'total': float(total),
        'carrito_count': count,
        'message': 'Producto eliminado del carrito'
    })


def verificar_sesion_carrito(request):
    """Verificar si el usuario tiene sesión activa para el checkout"""
    if request.user.is_authenticated:
        return JsonResponse({'autenticado': True, 'usuario': request.user.username})
    return JsonResponse({'autenticado': False})


# ==================== PAGO Y CHECKOUT ====================

@login_required
def proceso_pago(request):
    """Página de checkout/pago"""
    items = CarritoItem.objects.select_related('producto').filter(usuario=request.user)
    if not items:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('tienda:ver_carrito')
    
    total = sum(item.subtotal for item in items)
    perfil = getattr(request.user, 'perfil', None)
    
    context = {
        'items': items,
        'total': total,
        'perfil': perfil,
        'paypal_client_id': settings.PAYPAL_CLIENT_ID,
    }
    return render(request, 'tienda/pago.html', context)


@login_required
@require_POST
def procesar_pago(request):
    """Procesar el pago y crear la venta"""
    items = CarritoItem.objects.select_related('producto').filter(usuario=request.user)
    if not items:
        return JsonResponse({'success': False, 'error': 'Carrito vacío'})
    
    with transaction.atomic():
        # Verificar stock otra vez
        for item in items:
            if item.cantidad > item.producto.stock:
                return JsonResponse({
                    'success': False, 
                    'error': f'Stock insuficiente para {item.producto.nombre}'
                })
        
        total = sum(item.subtotal for item in items)
        
        # Crear venta
        venta = Venta.objects.create(
            usuario=request.user,
            total=total,
            estatus='pagado',
            direccion_envio=request.POST.get('direccion', ''),
            telefono_contacto=request.POST.get('telefono', ''),
            notas=request.POST.get('notas', '')
        )
        
        # Crear detalles y actualizar stock
        for item in items:
            DetalleVenta.objects.create(
                venta=venta,
                producto=item.producto,
                cantidad=item.cantidad,
                precio_unitario=item.producto.precio
            )
            # Reducir stock
            item.producto.stock -= item.cantidad
            item.producto.save()
        
        # Vaciar carrito
        items.delete()
    
    messages.success(request, f'¡Pedido #{venta.id} realizado con éxito!')
    return JsonResponse({'success': True, 'venta_id': venta.id})


# ==================== ADMINISTRACIÓN ====================

@login_required
def admin_productos(request):
    """Panel de administración de productos"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes acceso a esta sección.')
        return redirect('tienda:index')
    
    productos = Producto.objects.all().order_by('-fecha_creacion')
    categorias = Categoria.objects.all()
    
    context = {
        'productos': productos,
        'categorias': categorias,
    }
    return render(request, 'tienda/admin_productos.html', context)


@login_required
def admin_inventario(request):
    """Panel de administración de inventario"""
    if not request.user.is_staff:
        messages.error(request, 'No tienes acceso a esta sección.')
        return redirect('tienda:index')
    
    productos = Producto.objects.all().order_by('stock')
    
    # KPIs
    total_productos = productos.count()
    productos_sin_stock = productos.filter(stock=0).count()
    productos_bajo_stock = productos.filter(stock__lt=10, stock__gt=0).count()
    
    context = {
        'productos': productos,
        'total_productos': total_productos,
        'productos_sin_stock': productos_sin_stock,
        'productos_bajo_stock': productos_bajo_stock,
    }
    return render(request, 'tienda/admin_inventario.html', context)


@login_required
def admin_crear_producto(request):
    """Crear nuevo producto (vista simple)"""
    if not request.user.is_staff:
        return redirect('tienda:index')
    
    if request.method == 'POST':
        nombre = request.POST.get('nombre')
        categoria_id = request.POST.get('categoria')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        descripcion = request.POST.get('descripcion', '')
        
        from django.utils.text import slugify
        slug = slugify(nombre)
        
        Producto.objects.create(
            nombre=nombre,
            slug=slug,
            categoria_id=categoria_id,
            precio=precio,
            stock=stock,
            descripcion=descripcion
        )
        
        messages.success(request, f'Producto {nombre} creado exitosamente.')
        return redirect('tienda:admin_productos')
    
    categorias = Categoria.objects.all()
    return render(request, 'tienda/admin_crear_producto.html', {'categorias': categorias})


@login_required
def admin_ventas(request):
    """Panel de ventas"""
    if not request.user.is_staff:
        return redirect('tienda:index')
    
    ventas = Venta.objects.all().order_by('-fecha_venta')
    
    context = {
        'ventas': ventas,
    }
    return render(request, 'tienda/admin_ventas.html', context)


# ==================== CONTACTO ====================

@require_POST
def contacto(request):
    """Procesar formulario de contacto del footer"""
    nombre = request.POST.get('nombre', '').strip()
    email = request.POST.get('email', '').strip()
    mensaje = request.POST.get('mensaje', '').strip()
    
    if not nombre or not email or not mensaje:
        return JsonResponse({
            'success': False, 
            'error': 'Todos los campos son obligatorios'
        }, status=400)
    
    # Validar longitud mínima
    if len(mensaje) < 10:
        return JsonResponse({
            'success': False, 
            'error': 'El mensaje debe tener al menos 10 caracteres'
        }, status=400)
    
    # Guardar mensaje
    MensajeContacto.objects.create(
        nombre=nombre,
        email=email,
        mensaje=mensaje
    )
    
    return JsonResponse({
        'success': True, 
        'message': '¡Mensaje enviado correctamente! Nos contactaremos pronto.'
    })


# ==================== PAYPAL ====================

@login_required
def crear_orden_paypal(request):
    """Crear orden en PayPal - recalcula total desde DB"""
    items = CarritoItem.objects.select_related('producto').filter(usuario=request.user)
    if not items:
        return JsonResponse({'success': False, 'error': 'Carrito vacío'}, status=400)
    
    total = sum(item.subtotal for item in items)
    
    paypal_mode = 'sandbox' if settings.PAYPAL_MODE == 'sandbox' else 'live'
    base_url = f'https://api-m.{paypal_mode}.paypal.com' if paypal_mode == 'sandbox' else 'https://api-m.paypal.com'
    
    access_token = obtener_access_token_paypal()
    if not access_token:
        return JsonResponse({'success': False, 'error': 'Error de conexión con PayPal'}, status=500)
    
    url = f'{base_url}/v2/checkout/orders'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    data = {
        'intent': 'CAPTURE',
        'purchase_units': [{
            'amount': {
                'currency_code': 'MXN',
                'value': str(total)
            },
            'description': 'Compra en Vinatería Los 3 Hermanos'
        }],
        'application_context': {
            'return_url': request.build_absolute_uri('/pago/exito/'),
            'cancel_url': request.build_absolute_uri('/pago/')
        }
    }
    
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 201:
        order_data = response.json()
        return JsonResponse({
            'success': True,
            'order_id': order_data['id']
        })
    else:
        return JsonResponse({'success': False, 'error': 'Error al crear orden PayPal'}, status=500)


@login_required
def capturar_orden_paypal(request):
    """Capturar pago de PayPal - solo crear venta si COMPLETED"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)
    
    try:
        data = json.loads(request.body)
        order_id = data.get('order_id')
    except:
        return JsonResponse({'success': False, 'error': 'Datos inválidos'}, status=400)
    
    if not order_id:
        return JsonResponse({'success': False, 'error': 'Order ID requerido'}, status=400)
    
    items = CarritoItem.objects.select_related('producto').filter(usuario=request.user)
    if not items:
        return JsonResponse({'success': False, 'error': 'Carrito vacío'}, status=400)
    
    total = sum(item.subtotal for item in items)
    
    paypal_mode = 'sandbox' if settings.PAYPAL_MODE == 'sandbox' else 'live'
    base_url = f'https://api-m.{paypal_mode}.paypal.com' if paypal_mode == 'sandbox' else 'https://api-m.paypal.com'
    
    access_token = obtener_access_token_paypal()
    if not access_token:
        return JsonResponse({'success': False, 'error': 'Error de conexión con PayPal'}, status=500)
    
    url = f'{base_url}/v2/checkout/orders/{order_id}/capture'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    response = requests.post(url, headers=headers)
    
    if response.status_code == 201:
        capture_data = response.json()
        status = capture_data.get('status')
        
        if status != 'COMPLETED':
            return JsonResponse({'success': False, 'error': 'Pago no completado'}, status=400)
        
        with transaction.atomic():
            for item in items:
                if item.cantidad > item.producto.stock:
                    return JsonResponse({
                        'success': False, 
                        'error': f'Stock insuficiente para {item.producto.nombre}'
                    })
            
            venta = Venta.objects.create(
                usuario=request.user,
                total=total,
                estatus='pagado',
                direccion_envio=data.get('direccion', ''),
                telefono_contacto=data.get('telefono', ''),
                notas=data.get('notas', '')
            )
            
            for item in items:
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=item.producto,
                    cantidad=item.cantidad,
                    precio_unitario=item.producto.precio
                )
                item.producto.stock -= item.cantidad
                item.producto.save()
            
            items.delete()
        
        return JsonResponse({
            'success': True,
            'venta_id': venta.id
        })
    else:
        return JsonResponse({'success': False, 'error': 'Error al capturar pago'}, status=500)


def obtener_access_token_paypal():
    """Obtener token de acceso de PayPal"""
    paypal_mode = 'sandbox' if settings.PAYPAL_MODE == 'sandbox' else 'live'
    base_url = f'https://api-m.{paypal_mode}.paypal.com' if paypal_mode == 'sandbox' else 'https://api-m.paypal.com'
    
    client_id = settings.PAYPAL_CLIENT_ID
    secret = settings.PAYPAL_SECRET
    
    if not client_id or not secret:
        return None
    
    url = f'{base_url}/v1/oauth2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'client_credentials'}
    
    response = requests.post(url, headers=headers, data=data, auth=(client_id, secret))
    
    if response.status_code == 200:
        return response.json().get('access_token')
    return None


# ==================== VISTA DE ÉXITO ====================

@login_required
def pago_exitoso(request, venta_id):
    """Vista de éxito del pago - validación de propiedad"""
    venta = get_object_or_404(Venta, id=venta_id)
    
    if venta.usuario != request.user:
        return HttpResponseForbidden()
    
    detalles = DetalleVenta.objects.filter(venta=venta)
    
    context = {
        'venta': venta,
        'detalles': detalles,
    }
    return render(request, 'tienda/exito.html', context)


# ==================== PÁGINAS ESTÁTICAS ====================

def terminos_condiciones(request):
    """Página de términos y condiciones"""
    return render(request, 'tienda/terminos.html')


# ==================== PERFIL DE USUARIO ====================

@login_required
def mi_perfil(request):
    """Perfil del usuario con historial de pedidos"""
    ventas = Venta.objects.filter(usuario=request.user).prefetch_related(
        'detalles__producto'
    ).order_by('-fecha_venta')
    
    paginator = Paginator(ventas, 10)
    page_number = request.GET.get('page')
    ventas_page = paginator.get_page(page_number)
    
    perfil = getattr(request.user, 'perfil', None)
    
    context = {
        'ventas': ventas_page,
        'perfil': perfil,
    }
    return render(request, 'tienda/perfil.html', context)


# ==================== DESCARGA DE RECIBO PDF ====================

@login_required
def descargar_recibo_pdf(request, venta_id):
    """Generar y descargar recibo en PDF"""
    venta = get_object_or_404(Venta, id=venta_id)
    
    if venta.usuario != request.user:
        return HttpResponseForbidden()
    
    detalles = DetalleVenta.objects.filter(venta=venta).select_related('producto')
    perfil = getattr(request.user, 'perfil', None)
    
    context = {
        'venta': venta,
        'detalles': detalles,
        'perfil': perfil,
        'user': request.user,
    }
    
    html_string = render_to_string('tienda/recibo_pdf.html', context)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="recibo_orden_{venta_id}.pdf"'
    
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=500)
    
    return response