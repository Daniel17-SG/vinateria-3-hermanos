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
