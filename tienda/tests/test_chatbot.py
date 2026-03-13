import pytest
from django.urls import reverse

from tienda.models import Categoria, Producto


@pytest.mark.django_db
def test_chatbot_responde_saludo(client):
    url = reverse('tienda:chatbot_responder')
    response = client.post(
        url,
        data='{"mensaje": "hola"}',
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get('success') is True
    assert 'asistente' in data.get('respuesta', '').lower() or 'hola' in data.get('respuesta', '').lower()


@pytest.mark.django_db
def test_chatbot_recomienda_por_categoria(client):
    categoria = Categoria.objects.create(nombre='Tequila', slug='tequila')
    Producto.objects.create(
        nombre='Tequila Reposado Test',
        slug='tequila-reposado-test',
        categoria=categoria,
        precio='549.00',
        stock=7,
        activo=True,
    )

    url = reverse('tienda:chatbot_responder')
    response = client.post(
        url,
        data='{"mensaje": "quiero tequila"}',
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get('success') is True
    assert 'tequila' in data.get('respuesta', '').lower()
    assert 'tequila reposado test' in data.get('respuesta', '').lower()


@pytest.mark.django_db
def test_chatbot_aplica_presupuesto_maximo(client):
    categoria = Categoria.objects.create(nombre='Tequila', slug='tequila')
    Producto.objects.create(
        nombre='Tequila Economico',
        slug='tequila-economico',
        categoria=categoria,
        precio='450.00',
        stock=5,
        activo=True,
    )
    Producto.objects.create(
        nombre='Tequila Premium Alto',
        slug='tequila-premium-alto',
        categoria=categoria,
        precio='1200.00',
        stock=5,
        activo=True,
    )

    url = reverse('tienda:chatbot_responder')
    response = client.post(
        url,
        data='{"mensaje": "quiero tequila hasta 500"}',
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    assert data.get('success') is True
    assert 'tequila economico' in data.get('respuesta', '').lower()
    assert 'tequila premium alto' not in data.get('respuesta', '').lower()


@pytest.mark.django_db
def test_chatbot_regla_fiesta_prioriza_valor(client):
    categoria = Categoria.objects.create(nombre='Ron', slug='ron')
    Producto.objects.create(
        nombre='Ron Fiesta Valor',
        slug='ron-fiesta-valor',
        categoria=categoria,
        precio='350.00',
        stock=20,
        activo=True,
    )
    Producto.objects.create(
        nombre='Ron Fiesta Premium',
        slug='ron-fiesta-premium',
        categoria=categoria,
        precio='900.00',
        stock=4,
        activo=True,
    )

    url = reverse('tienda:chatbot_responder')
    response = client.post(
        url,
        data='{"mensaje": "busco ron para fiesta"}',
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    texto = data.get('respuesta', '').lower()
    assert data.get('success') is True
    assert 'ron fiesta valor' in texto
    assert 'ocasión fiesta' in data.get('respuesta', '')


@pytest.mark.django_db
def test_chatbot_muestra_inventario_completo(client):
    tequila = Categoria.objects.create(nombre='Tequila', slug='tequila')
    vodka = Categoria.objects.create(nombre='Vodka', slug='vodka')

    Producto.objects.create(
        nombre='Tequila Inventario',
        slug='tequila-inventario',
        categoria=tequila,
        precio='500.00',
        stock=3,
        activo=True,
    )
    Producto.objects.create(
        nombre='Vodka Inventario',
        slug='vodka-inventario',
        categoria=vodka,
        precio='390.00',
        stock=6,
        activo=True,
    )

    url = reverse('tienda:chatbot_responder')
    response = client.post(
        url,
        data='{"mensaje": "quiero ver todos los productos"}',
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    texto = data.get('respuesta', '').lower()
    assert data.get('success') is True
    assert 'inventario actual' in texto
    assert 'tequila inventario' in texto
    assert 'vodka inventario' in texto


@pytest.mark.django_db
def test_chatbot_informa_metodos_pago(client):
    url = reverse('tienda:chatbot_responder')
    response = client.post(
        url,
        data='{"mensaje": "que metodos de pago tienen"}',
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    texto = data.get('respuesta', '').lower()
    assert data.get('success') is True
    assert 'paypal' in texto
    assert 'contra entrega' in texto


@pytest.mark.django_db
def test_chatbot_responde_despedida(client):
    url = reverse('tienda:chatbot_responder')
    response = client.post(
        url,
        data='{"mensaje": "gracias, adios"}',
        content_type='application/json'
    )

    assert response.status_code == 200
    data = response.json()
    texto = data.get('respuesta', '').lower()
    assert data.get('success') is True
    assert 'gracias por visitar' in texto or 'excelente día' in texto
