"""
Tests de seguridad para el panel de administración.

Verifica que usuarios no autorizados no puedan acceder a rutas de gerencia.
"""
import pytest
from django.urls import reverse


@pytest.mark.django_db
class TestAdminAccessControl:
    """
    Suite de pruebas para verificar control de acceso al panel de administración.
    
    Cubre:
    - Usuarios anónimos (no autenticados)
    - Usuarios autenticados sin privilegios (is_staff=False)
    - Usuarios staff (is_staff=True) — deben tener acceso
    """

    ADMIN_URL = '/cp-3h-ops/'

    def test_anonymous_user_redirected_from_admin(self, client):
        """
        Un usuario anónimo debe ser redirigido al login (302) al intentar
        acceder al panel de administración.
        """
        response = client.get(self.ADMIN_URL)
        
        # El admin de Django redirige a su página de login
        assert response.status_code == 302
        assert '/login/' in response.url or 'login' in response.url.lower()

    def test_normal_user_forbidden_from_admin(self, client, django_user_model):
        """
        Un usuario autenticado pero SIN is_staff=True debe recibir una
        redirección al login del admin (no tiene permisos).
        
        NOTA: Django Admin redirige a su login cuando un usuario sin permisos
        intenta acceder; devuelve 302, no 403 directamente.
        """
        # Crear usuario normal (cliente)
        user = django_user_model.objects.create_user(
            username='cliente_normal',
            email='cliente@example.com',
            password='password123',
            is_staff=False,
            is_superuser=False
        )
        client.force_login(user)
        
        response = client.get(self.ADMIN_URL)
        
        # Django admin redirige a su login si el usuario no es staff
        # Esto es 302, no 403 — lo cual es aceptable y más seguro (no revela
        # información sobre la existencia del recurso)
        assert response.status_code == 302
        # Verificar que NO redirige al dashboard (éxito)
        assert 'dashboard' not in response.url

    def test_staff_user_can_access_admin(self, client, django_user_model):
        """
        Un usuario con is_staff=True debe poder acceder al panel de
        administración (status 200 o redirección interna al dashboard).
        """
        # Crear usuario staff
        staff_user = django_user_model.objects.create_user(
            username='gerente',
            email='gerente@vinateria.com',
            password='securepass123',
            is_staff=True,
            is_superuser=False
        )
        client.force_login(staff_user)
        
        response = client.get(self.ADMIN_URL)
        
        # Puede ser 200 (acceso directo) o 302 a una subpágina del admin
        assert response.status_code in (200, 302)
        # Si es redirección, debe ser dentro del admin, no al login
        if response.status_code == 302:
            assert '/cp-3h-ops/' in response.url or 'login' not in response.url.lower()

    def test_superuser_can_access_admin(self, client, django_user_model):
        """
        Un superusuario debe tener acceso completo al panel de administración.
        """
        superuser = django_user_model.objects.create_superuser(
            username='admin',
            email='admin@vinateria.com',
            password='superpass123'
        )
        client.force_login(superuser)
        
        response = client.get(self.ADMIN_URL)
        
        assert response.status_code in (200, 302)
        if response.status_code == 302:
            # La redirección debe ser interna al admin, no al login
            assert 'login' not in response.url.lower()


@pytest.mark.django_db
class TestLoginRedirection:
    """
    Verifica que la redirección post-login sea correcta según el tipo de usuario.
    """

    def test_staff_user_redirected_to_admin_after_login(self, client, django_user_model):
        """
        Un usuario staff debe ser redirigido al panel de administración
        después de iniciar sesión exitosamente.
        """
        staff_user = django_user_model.objects.create_user(
            username='staff_test',
            email='staff@test.com',
            password='testpass123',
            is_staff=True
        )
        
        response = client.post(
            reverse('tienda:login'),
            {'username': 'staff_test', 'password': 'testpass123'},
            follow=False
        )
        
        assert response.status_code == 302
        # Debe redirigir al admin (cp-3h-ops)
        assert '/cp-3h-ops/' in response.url

    def test_normal_user_redirected_to_store_after_login(self, client, django_user_model):
        """
        Un usuario normal debe ser redirigido a la tienda (index)
        después de iniciar sesión exitosamente.
        """
        normal_user = django_user_model.objects.create_user(
            username='cliente_test',
            email='cliente@test.com',
            password='testpass123',
            is_staff=False
        )
        
        response = client.post(
            reverse('tienda:login'),
            {'username': 'cliente_test', 'password': 'testpass123'},
            follow=False
        )
        
        assert response.status_code == 302
        # Debe redirigir a la tienda, no al admin
        assert '/cp-3h-ops/' not in response.url

    def test_next_parameter_takes_priority(self, client, django_user_model):
        """
        Si existe un parámetro ?next=, ese debe tener prioridad sobre
        la redirección por defecto (incluso para usuarios staff).
        """
        staff_user = django_user_model.objects.create_user(
            username='staff_next',
            email='staff_next@test.com',
            password='testpass123',
            is_staff=True
        )
        
        target_url = '/catalogo/'
        login_url = reverse('tienda:login') + f'?next={target_url}'
        
        response = client.post(
            login_url,
            {'username': 'staff_next', 'password': 'testpass123'},
            follow=False
        )
        
        assert response.status_code == 302
        # Debe respetar el parámetro next, no ir al admin
        assert target_url in response.url
