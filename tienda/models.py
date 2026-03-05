from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static


class Categoria(models.Model):
    """Categorías de productos (Tequila, Whisky, Brandy, Vodka, Ron)"""
    nombre = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    
    class Meta:
        verbose_name_plural = "Categorías"
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Producto(models.Model):
    """Productos de la vinatería"""
    nombre = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    descripcion = models.TextField(blank=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)
    imagen = models.ImageField(upload_to='productos/%Y/%m/', blank=True, null=True)
    activo = models.BooleanField(default=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-fecha_creacion']
    
    def __str__(self):
        return self.nombre

    @property
    def imagen_url(self):
        fallback = static('tienda/imagenes/reposado.png')
        if not self.imagen:
            return fallback

        try:
            if self.imagen.name and self.imagen.storage.exists(self.imagen.name):
                return self.imagen.url
        except Exception:
            return fallback

        return fallback


class PerfilCliente(models.Model):
    """Perfil extendido para clientes"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='perfil')
    telefono = models.CharField(max_length=20, blank=True)
    direccion = models.TextField(blank=True)
    ciudad = models.CharField(max_length=100, blank=True)
    cp = models.CharField(max_length=10, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Perfil de {self.user.username}"


class CarritoItem(models.Model):
    """Items del carrito de compras"""
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carrito')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    fecha_agregado = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('usuario', 'producto')
        ordering = ['-fecha_agregado']
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
    @property
    def subtotal(self):
        return self.producto.precio * self.cantidad


class Venta(models.Model):
    """Registro de ventas"""
    ESTATUS_CHOICES = [
        ('pendiente', 'Pendiente de Pago'),
        ('pagado', 'Pagado'),
        ('enviado', 'Enviado'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    ]
    
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ventas')
    fecha_venta = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    estatus = models.CharField(max_length=20, choices=ESTATUS_CHOICES, default='pendiente')
    direccion_envio = models.TextField()
    telefono_contacto = models.CharField(max_length=20)
    notas = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-fecha_venta']
    
    def __str__(self):
        return f"Venta #{self.id} - {self.usuario.username} - {self.estatus}"


class DetalleVenta(models.Model):
    """Detalles de cada producto en una venta"""
    venta = models.ForeignKey(Venta, related_name='detalles', on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"
    
    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad


class MensajeContacto(models.Model):
    """Mensajes del formulario de contacto del footer"""
    nombre = models.CharField(max_length=100)
    email = models.EmailField()
    mensaje = models.TextField()
    fecha_envio = models.DateTimeField(auto_now_add=True)
    leido = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"Mensaje de {self.nombre} - {self.fecha_envio.strftime('%Y-%m-%d')}"
