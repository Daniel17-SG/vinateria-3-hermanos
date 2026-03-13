from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.views.decorators.cache import never_cache
from django.db import transaction, IntegrityError, DatabaseError
from django.db.models import Q
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.http import url_has_allowed_host_and_scheme
from xhtml2pdf import pisa
from django.http import HttpResponse
from django_ratelimit.decorators import ratelimit
import requests
import json
import logging
from requests.exceptions import RequestException
from decimal import Decimal, InvalidOperation
import re

logger = logging.getLogger(__name__)

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
            raw_password = form.cleaned_data.get('password1')
            # Autenticar para que Django asigne backend al usuario antes de hacer login
            user = authenticate(request, username=user.username, password=raw_password)
            if user is not None:
                login(request, user)
            else:
                messages.warning(request, 'Tu cuenta fue creada, inicia sesión con tus credenciales.')
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
        if request.user.is_staff or request.user.is_superuser:
            return redirect('tienda:admin_productos')
        return redirect('tienda:catalogo')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                
                # Redirección condicional: admin → panel, usuario → tienda
                next_url = request.POST.get('next') or request.GET.get('next')
                if next_url and url_has_allowed_host_and_scheme(
                    next_url,
                    allowed_hosts={request.get_host()},
                    require_https=request.is_secure(),
                ):
                    redirect_url = next_url
                elif user.is_staff or user.is_superuser:
                    redirect_url = 'tienda:admin_productos'
                else:
                    redirect_url = settings.LOGIN_REDIRECT_URL
                
                messages.success(request, f'¡Bienvenido de nuevo, {username}!')
                return redirect(redirect_url)
        messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'tienda/login.html', {'form': form})


@never_cache
def logout_view(request):
    """Cerrar sesión - Destrucción total de sesión y cookies"""
    request.session.flush()  # Destrucción física en BD
    logout(request)  # Destrucción lógica
    
    messages.info(request, 'Has cerrado sesión correctamente.')
    
    response = redirect('tienda:index')
    
    # Destrucción de cookies
    response.delete_cookie(settings.SESSION_COOKIE_NAME)
    response.delete_cookie('csrftoken')
    
    # Cabeceras anti-caché
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
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Cantidad inválida'})
    
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
    try:
        cantidad = int(request.POST.get('cantidad', 1))
    except (ValueError, TypeError):
        return JsonResponse({'success': False, 'error': 'Cantidad inválida'})
    
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
        producto_ids = [item.producto_id for item in items]
        productos_bloqueados = Producto.objects.select_for_update().filter(
            id__in=producto_ids
        )
        productos_dict = {p.id: p for p in productos_bloqueados}
        
        for item in items:
            producto = productos_dict.get(item.producto_id)
            if not producto or item.cantidad > producto.stock:
                return JsonResponse({
                    'success': False, 
                    'error': f'Stock insuficiente para {item.producto.nombre}'
                })
        
        total = sum(item.subtotal for item in items)
        
        venta = Venta.objects.create(
            usuario=request.user,
            total=total,
            estatus='pagado',
            direccion_envio=request.POST.get('direccion', ''),
            telefono_contacto=request.POST.get('telefono', ''),
            notas=request.POST.get('notas', '')
        )
        
        for item in items:
            producto = productos_dict[item.producto_id]
            DetalleVenta.objects.create(
                venta=venta,
                producto=producto,
                cantidad=item.cantidad,
                precio_unitario=producto.precio
            )
            producto.stock -= item.cantidad
            producto.save()
        
        items.delete()
    
    messages.success(request, f'¡Pedido #{venta.id} realizado con éxito!')
    return JsonResponse({'success': True, 'venta_id': venta.id})


# ==================== ADMINISTRACIÓN ====================

@login_required
@staff_member_required
def admin_productos(request):
    """Panel de administración de productos"""
    productos = Producto.objects.all().order_by('-fecha_creacion')
    categorias = Categoria.objects.all()
    
    context = {
        'productos': productos,
        'categorias': categorias,
    }
    return render(request, 'tienda/admin_productos.html', context)


@login_required
@staff_member_required
def admin_inventario(request):
    """Panel de administración de inventario"""
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
@staff_member_required
def admin_crear_producto(request):
    """Crear nuevo producto con validación de tipos"""
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        categoria_id = request.POST.get('categoria')
        precio_str = request.POST.get('precio', '0')
        stock_str = request.POST.get('stock', '0')
        descripcion = request.POST.get('descripcion', '')
        
        if not nombre:
            messages.error(request, 'El nombre del producto es obligatorio.')
            return redirect('tienda:admin_crear_producto')
        
        try:
            precio = Decimal(precio_str)
            stock = int(stock_str)
            if precio < 0 or stock < 0:
                raise ValueError("Valores negativos no permitidos")
        except (ValueError, InvalidOperation) as e:
            logger.warning(f"Intento de inyección de tipos en admin_crear_producto: {e} - Usuario: {request.user}")
            messages.error(request, 'Precio y stock deben ser valores numéricos válidos.')
            return redirect('tienda:admin_crear_producto')
        
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
@staff_member_required
def admin_ventas(request):
    """Panel de ventas"""
    ventas = Venta.objects.all().order_by('-fecha_venta')
    
    context = {
        'ventas': ventas,
    }
    return render(request, 'tienda/admin_ventas.html', context)


# ==================== CONTACTO ====================

def _normalizar_texto_chatbot(texto):
    """Normaliza texto libre para facilitar matching de intenciones."""
    texto = (texto or '').lower().strip()
    return re.sub(r'\s+', ' ', texto)


def _detectar_categoria_chatbot(mensaje):
    """Detecta categoría de destilado mencionada por el usuario."""
    mapping = {
        'tequila': ['tequila', 'reposado', 'anejo', 'añejo', 'blanco'],
        'whisky': ['whisky', 'whiskey', 'bourbon', 'scotch'],
        'brandy': ['brandy', 'cognac'],
        'vodka': ['vodka'],
        'ron': ['ron', 'rum'],
    }

    for slug, keywords in mapping.items():
        if any(k in mensaje for k in keywords):
            return slug
    return None


def _extraer_presupuesto_chatbot(mensaje):
    """Extrae rango de presupuesto desde texto libre."""
    numeros = [Decimal(n) for n in re.findall(r'\d{2,6}(?:\.\d{1,2})?', mensaje)]
    if not numeros:
        return None, None

    if ('entre' in mensaje or 'rango' in mensaje) and len(numeros) >= 2:
        low = min(numeros[0], numeros[1])
        high = max(numeros[0], numeros[1])
        return low, high

    if any(k in mensaje for k in ['menos de', 'maximo', 'máximo', 'hasta', 'tope']):
        return None, numeros[0]

    if any(k in mensaje for k in ['mas de', 'más de', 'desde', 'minimo', 'mínimo']):
        return numeros[0], None

    if any(k in mensaje for k in ['presupuesto', 'cuesta', 'costo', 'barato', 'económico', 'economico']):
        return None, numeros[0]

    return None, None


def _respuesta_reglas_negocio_chatbot(mensaje):
    """Aplica reglas de negocio de vinatería para recomendar productos."""
    categoria_slug = _detectar_categoria_chatbot(mensaje)
    presupuesto_min, presupuesto_max = _extraer_presupuesto_chatbot(mensaje)

    ocasion = None
    if any(k in mensaje for k in ['regalo', 'premium', 'especial', 'aniversario']):
        ocasion = 'regalo'
    elif any(k in mensaje for k in ['fiesta', 'reunion', 'reunión', 'evento', 'boda']):
        ocasion = 'fiesta'
    elif any(k in mensaje for k in ['coctel', 'cocteles', 'cóctel', 'mezclar', 'mixologia', 'mixología']):
        ocasion = 'coctel'

    sabor = None
    if any(k in mensaje for k in ['suave', 'ligero', 'fino']):
        sabor = 'suave'
    elif any(k in mensaje for k in ['fuerte', 'intenso', 'robusto']):
        sabor = 'intenso'
    elif any(k in mensaje for k in ['dulce', 'caramelo', 'vainilla']):
        sabor = 'dulce'

    activar_reglas = any([categoria_slug, presupuesto_min, presupuesto_max, ocasion, sabor])
    if not activar_reglas:
        return None

    productos = Producto.objects.filter(activo=True, stock__gt=0).select_related('categoria')

    if categoria_slug:
        productos = productos.filter(categoria__slug__iexact=categoria_slug)

    if ocasion == 'coctel' and not categoria_slug:
        productos = productos.filter(categoria__slug__in=['vodka', 'ron', 'tequila'])

    if presupuesto_min is not None:
        productos = productos.filter(precio__gte=presupuesto_min)
    if presupuesto_max is not None:
        productos = productos.filter(precio__lte=presupuesto_max)

    if ocasion == 'regalo':
        productos = productos.order_by('-precio', '-fecha_creacion')
    elif ocasion == 'fiesta':
        productos = productos.order_by('precio', '-stock')
    elif ocasion == 'coctel':
        productos = productos.order_by('precio', '-fecha_creacion')
    else:
        productos = productos.order_by('-fecha_creacion')

    sugeridos = list(productos[:3])
    if not sugeridos:
        return (
            'Con esas reglas no encontré productos disponibles en este momento. '
            'Si quieres, ajusta tu presupuesto o categoría y te propongo otras opciones.'
        )

    etiquetas = []
    if categoria_slug:
        etiquetas.append(f"tipo {categoria_slug}")
    if presupuesto_max is not None and presupuesto_min is None:
        etiquetas.append(f"presupuesto hasta ${presupuesto_max}")
    if presupuesto_min is not None and presupuesto_max is not None:
        etiquetas.append(f"rango ${presupuesto_min}-${presupuesto_max}")
    if ocasion:
        etiquetas.append(f"ocasión {ocasion}")
    if sabor:
        etiquetas.append(f"perfil {sabor}")

    encabezado = 'Te recomiendo estas opciones según tus reglas de negocio'
    if etiquetas:
        encabezado += f" ({', '.join(etiquetas)}):"
    else:
        encabezado += ':'

    lista = '\n'.join([f"- {p.nombre} (${p.precio})" for p in sugeridos])

    tips = {
        'suave': 'Tip de sommelier: para un perfil suave, sírvelo ligeramente frío en copa corta.',
        'intenso': 'Tip de sommelier: para perfil intenso, úsalo en las rocas para abrir aromas.',
        'dulce': 'Tip de maridaje: combina perfiles dulces con chocolate amargo o postres secos.',
    }
    tip = tips.get(sabor)

    respuesta = f"{encabezado}\n{lista}\n\nSolo vendemos a mayores de edad (+18)."
    if tip:
        respuesta = f"{respuesta}\n{tip}"
    return respuesta


def _respuesta_catalogo(mensaje):
    """Intenta recomendar productos/categorias con base en el mensaje."""
    if len(mensaje) < 2:
        return None

    categorias = list(
        Categoria.objects.filter(activo=True).values_list('slug', 'nombre')
    )

    for slug, nombre in categorias:
        if slug and slug.lower() in mensaje:
            productos = Producto.objects.filter(
                activo=True,
                stock__gt=0,
                categoria__slug=slug,
            ).order_by('-fecha_creacion')[:3]

            if productos:
                lista = '\n'.join([f"- {p.nombre} (${p.precio})" for p in productos])
                return (
                    f"Claro, te recomiendo estos productos de {nombre}:\n{lista}\n\n"
                    "Puedes verlos en el catálogo y agregarlos al carrito desde ahí."
                )

    sugeridos = Producto.objects.filter(
        activo=True,
        stock__gt=0,
    ).filter(
        Q(nombre__icontains=mensaje)
        | Q(descripcion__icontains=mensaje)
        | Q(categoria__nombre__icontains=mensaje)
    ).select_related('categoria')[:3]

    if sugeridos:
        lista = '\n'.join([f"- {p.nombre} (${p.precio})" for p in sugeridos])
        return (
            "Encontré estas opciones para ti:\n"
            f"{lista}\n\n"
            "Si quieres, también te puedo sugerir por categoría: tequila, whisky, brandy, vodka o ron."
        )

    return None


def _respuesta_intencion_general(mensaje):
    """Respuestas rápidas para preguntas frecuentes de tienda."""
    categorias = ', '.join(
        Categoria.objects.filter(activo=True)
        .values_list('nombre', flat=True)
        .order_by('nombre')
    ) or 'Tequila, Whisky, Brandy, Vodka y Ron'

    respuestas = [
        (
            ['hola', 'buenas', 'que tal', 'saludos'],
            '¡Hola! Soy el asistente de Vinatería Los 3 Hermanos. ¿Buscas una recomendación o ayuda con tu pedido?',
        ),
        (
            ['horario', 'abren', 'cierran', 'abierto'],
            'Nuestro horario es: Lun-Sáb 9:00-21:00 y Dom 10:00-20:00.',
        ),
        (
            ['ubicacion', 'ubicación', 'direccion', 'dirección', 'donde', 'dónde'],
            'Estamos en el Centro Histórico, Ciudad de México. También puedes ver el mapa en el pie de página.',
        ),
        (
            ['envio', 'envío', 'entrega', 'domicilio'],
            'Tenemos envío gratis en compras mayores a $1,500. El tiempo de entrega depende de tu zona.',
        ),
        (
            ['pago', 'paypal', 'tarjeta', 'metodo de pago', 'método de pago'],
            'Puedes finalizar tu compra desde la sección de pago y usar PayPal de forma segura.',
        ),
        (
            ['catalogo', 'catálogo', 'productos', 'categorias', 'categorías'],
            f'En catálogo manejamos: {categorias}. Dime una categoría y te recomiendo opciones.',
        ),
        (
            ['contacto', 'telefono', 'teléfono', 'correo', 'email'],
            'Puedes escribirnos desde el formulario de contacto en el footer y te responderemos pronto.',
        ),
    ]

    for keywords, respuesta in respuestas:
        if any(k in mensaje for k in keywords):
            return respuesta

    return (
        'Puedo ayudarte con recomendaciones, categorías, horario, ubicación, envíos y pagos. '
        'Cuéntame qué necesitas y te apoyo.'
    )


@require_POST
@ratelimit(key='ip', rate='20/m', method='POST', block=True)
def chatbot_responder(request):
    """Endpoint JSON para responder mensajes del chatbot web."""
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'success': False, 'error': 'Solicitud inválida'}, status=400)

    mensaje = _normalizar_texto_chatbot(data.get('mensaje'))
    if len(mensaje) < 2:
        return JsonResponse({
            'success': False,
            'error': 'Escribe un mensaje un poco más descriptivo.'
        }, status=400)

    respuesta_reglas = _respuesta_reglas_negocio_chatbot(mensaje)
    if respuesta_reglas:
        respuesta = respuesta_reglas
    else:
        respuesta_catalogo = _respuesta_catalogo(mensaje)
        if respuesta_catalogo:
            respuesta = respuesta_catalogo
        else:
            respuesta = _respuesta_intencion_general(mensaje)

    return JsonResponse({
        'success': True,
        'respuesta': respuesta,
    })

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

def obtener_config_paypal():
    """Resolver modo y base URL de PayPal de forma segura."""
    mode = (getattr(settings, 'PAYPAL_MODE', 'sandbox') or 'sandbox').strip().lower()
    if mode not in {'sandbox', 'live'}:
        logger.warning(f"PAYPAL_MODE inválido '{mode}'. Se usará sandbox.")
        mode = 'sandbox'

    base_url = 'https://api-m.sandbox.paypal.com' if mode == 'sandbox' else 'https://api-m.paypal.com'
    return mode, base_url

@login_required
@require_POST
def crear_orden_paypal(request):
    """Crear orden en PayPal - recalcula total desde DB"""
    items = CarritoItem.objects.select_related('producto').filter(usuario=request.user)
    if not items:
        return JsonResponse({'success': False, 'error': 'Carrito vacío'}, status=400)
    
    total = sum(item.subtotal for item in items)
    
    _, base_url = obtener_config_paypal()
    
    try:
        access_token = obtener_access_token_paypal()
        if not access_token:
            return JsonResponse({
                'success': False,
                'error': 'No fue posible autenticar con PayPal. Verifica credenciales sandbox/live en Render.'
            }, status=502)
    except RequestException as e:
        logger.error(f"Error de conexión PayPal en crear_orden: {e}")
        return JsonResponse({'success': False, 'error': 'Error de conexión con el servidor de pagos'}, status=503)
    
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
    
    try:
        response = requests.post(url, headers=headers, json=data, timeout=15)
    except RequestException as e:
        logger.error(f"Timeout o error de red PayPal en crear_orden: {e}")
        return JsonResponse({'success': False, 'error': 'Tiempo de espera agotado. Intenta de nuevo.'}, status=503)
    
    if response.status_code == 201:
        order_data = response.json()
        return JsonResponse({
            'success': True,
            'order_id': order_data['id']
        })
    else:
        logger.error(f"Error PayPal crear orden - Status: {response.status_code}, Response: {response.text}")
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
    
    total_db = sum(item.subtotal for item in items)
    
    _, base_url = obtener_config_paypal()
    
    try:
        access_token = obtener_access_token_paypal()
        if not access_token:
            return JsonResponse({'success': False, 'error': 'Error de conexión con PayPal'}, status=500)
    except RequestException as e:
        logger.error(f"Error de conexión PayPal en capturar: {e}")
        return JsonResponse({'success': False, 'error': 'Error de conexión con el servidor de pagos'}, status=503)
    
    url = f'{base_url}/v2/checkout/orders/{order_id}/capture'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    
    try:
        response = requests.post(url, headers=headers, timeout=15)
    except RequestException as e:
        logger.error(f"Timeout o error de red PayPal en capturar: {e}")
        return JsonResponse({'success': False, 'error': 'Tiempo de espera agotado. Intenta de nuevo.'}, status=503)
    
    if response.status_code == 201:
        capture_data = response.json()
        status = capture_data.get('status')
        
        if status != 'COMPLETED':
            return JsonResponse({'success': False, 'error': 'Pago no completado'}, status=400)
        
        paypal_amount = None
        try:
            purchase_unit = capture_data.get('purchase_units', [{}])[0]
            payments = purchase_unit.get('payments', {})
            captures = payments.get('captures', [{}])[0]
            paypal_amount = Decimal(captures.get('amount', {}).get('value', '0'))
        except (KeyError, IndexError, InvalidOperation) as e:
            logger.error(f"Error al parsear monto de PayPal: {e}")
            return JsonResponse({'success': False, 'error': 'Error al verificar el pago'}, status=500)
        
        tolerance = Decimal('0.01')
        if abs(paypal_amount - total_db) > tolerance:
            logger.critical(
                f"ALERTA DE SEGURIDAD: Manipulación de precio detectada. "
                f"Usuario: {request.user.username}, OrderID: {order_id}, "
                f"Total DB: {total_db}, Total PayPal: {paypal_amount}"
            )
            return JsonResponse({
                'success': False, 
                'error': 'Error de validación del pago. Contacta al administrador.'
            }, status=400)
        
        with transaction.atomic():
            producto_ids = [item.producto_id for item in items]
            productos_bloqueados = Producto.objects.select_for_update().filter(
                id__in=producto_ids
            )
            productos_dict = {p.id: p for p in productos_bloqueados}
            
            for item in items:
                producto = productos_dict.get(item.producto_id)
                if not producto or item.cantidad > producto.stock:
                    return JsonResponse({
                        'success': False, 
                        'error': f'Stock insuficiente para {item.producto.nombre}'
                    })
            
            venta = Venta.objects.create(
                usuario=request.user,
                total=total_db,
                estatus='pagado',
                direccion_envio=data.get('direccion', ''),
                telefono_contacto=data.get('telefono', ''),
                notas=data.get('notas', '')
            )
            
            for item in items:
                producto = productos_dict[item.producto_id]
                DetalleVenta.objects.create(
                    venta=venta,
                    producto=producto,
                    cantidad=item.cantidad,
                    precio_unitario=producto.precio
                )
                producto.stock -= item.cantidad
                producto.save()
            
            items.delete()
        
        return JsonResponse({
            'success': True,
            'venta_id': venta.id
        })
    else:
        return JsonResponse({'success': False, 'error': 'Error al capturar pago'}, status=500)


def obtener_access_token_paypal():
    """Obtener token de acceso de PayPal"""
    mode, base_url = obtener_config_paypal()
    
    client_id = (settings.PAYPAL_CLIENT_ID or '').strip()
    secret = (settings.PAYPAL_SECRET or '').strip()
    
    if not client_id or not secret:
        logger.error(
            f"PayPal credentials no configuradas (mode={mode}, "
            f"client_id_len={len(client_id)}, secret_len={len(secret)})"
        )
        return None
    
    logger.info(
        f"Solicitando access token PayPal (mode={mode}, base_url={base_url}, "
        f"client_id_prefix={client_id[:8]}..., client_id_len={len(client_id)}, secret_len={len(secret)})"
    )
    
    url = f'{base_url}/v1/oauth2/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {'grant_type': 'client_credentials'}
    
    try:
        response = requests.post(url, headers=headers, data=data, auth=(client_id, secret), timeout=15)
    except RequestException as e:
        logger.error(f"Timeout o error de red al obtener access token PayPal: {e}")
        return None
    
    if response.status_code == 200:
        return response.json().get('access_token')

    paypal_debug_id = response.headers.get('paypal-debug-id', 'N/A')
    response_preview = (response.text or '')[:600]
    logger.error(
        f"Error al obtener access token PayPal - Status: {response.status_code}, "
        f"mode={mode}, paypal-debug-id={paypal_debug_id}, response={response_preview}"
    )
    if response.status_code == 401:
        logger.error(
            "PayPal 401 Unauthorized: verifica que PAYPAL_CLIENT_ID/PAYPAL_SECRET "
            "correspondan al mismo modo (sandbox/live) y no tengan espacios/comillas extra."
        )
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