import pytest
from django.urls import reverse

from tienda.models import Producto, Categoria, CarritoItem


@pytest.mark.django_db
def test_add_product_to_cart(client, django_user_model):
    # Create user and login
    user = django_user_model.objects.create_user(username='u', email='u@example.com', password='pass')
    client.login(username='u', password='pass')

    # Create category and product
    cat = Categoria.objects.create(nombre='TestCat', slug='testcat')
    product = Producto.objects.create(
        nombre='Vino Test',
        slug='vino-test',
        categoria=cat,
        precio='100.00',
        stock=10,
        activo=True
    )

    url = reverse('tienda:agregar_carrito', args=[product.id])
    resp = client.post(url, {'cantidad': 1})
    assert resp.status_code == 200
    data = resp.json()
    assert data.get('success') is True

    assert CarritoItem.objects.filter(usuario=user, producto=product).exists()
    item = CarritoItem.objects.get(usuario=user, producto=product)
    assert item.cantidad == 1
