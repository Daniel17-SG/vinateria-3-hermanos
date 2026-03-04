from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import path
from django.shortcuts import render
from django.db.models import Sum, Count, Q
from datetime import datetime, timedelta
from .models import Categoria, Producto, PerfilCliente, CarritoItem, Venta, DetalleVenta, MensajeContacto


class VinateriaAdminSite(AdminSite):
    site_header = "Vinatería Los 3 Hermanos"
    site_title = "Panel de Control"
    index_title = "Centro de Mando"
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('', self.admin_view(self.dashboard_view), name='dashboard'),
        ]
        return custom_urls + urls
    
    def dashboard_view(self, request):
        from django.db.models.functions import TruncDate
        
        hoy = datetime.now().date()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        inicio_mes = hoy.replace(day=1)
        
        # KPIs de Ventas
        ventas_hoy = Venta.objects.filter(fecha_venta__date=hoy, estatus='pagado').aggregate(
            total=Sum('total'), count=Count('id'))
        ventas_semana = Venta.objects.filter(fecha_venta__date__gte=inicio_semana, estatus='pagado').aggregate(
            total=Sum('total'), count=Count('id'))
        ventas_mes = Venta.objects.filter(fecha_venta__date__gte=inicio_mes, estatus='pagado').aggregate(
            total=Sum('total'), count=Count('id'))
        
        ingresos_totales = Venta.objects.filter(estatus='pagado').aggregate(total=Sum('total'))['total'] or 0
        
        # Productos bajo stock
        productos_bajo_stock = Producto.objects.filter(stock__lt=10, activo=True).count()
        productos_sin_stock = Producto.objects.filter(stock=0, activo=True).count()
        
        # Ventas últimos 7 días para gráfico
        ventas_diarias = Venta.objects.filter(
            fecha_venta__date__gte=hoy - timedelta(days=6),
            estatus='pagado'
        ).annotate(dia=TruncDate('fecha_venta')).values('dia').annotate(
            total=Sum('total'), cantidad=Count('id')
        ).order_by('dia')
        
        # Categorías más vendidas
        categorias_vendidas = DetalleVenta.objects.values(
            'producto__categoria__nombre'
        ).annotate(
            total_vendido=Sum('cantidad')
        ).order_by('-total_vendido')[:5]
        
        context = {
            **self.each_context(request),
            'ventas_hoy': ventas_hoy,
            'ventas_semana': ventas_semana,
            'ventas_mes': ventas_mes,
            'ingresos_totales': ingresos_totales,
            'productos_bajo_stock': productos_bajo_stock,
            'productos_sin_stock': productos_sin_stock,
            'ventas_diarias': list(ventas_diarias),
            'categorias_vendidas': list(categorias_vendidas),
        }
        return render(request, 'admin/dashboard.html', context)


admin_site = VinateriaAdminSite(name='vinateria_admin')
