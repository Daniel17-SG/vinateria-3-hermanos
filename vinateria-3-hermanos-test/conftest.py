import pytest


@pytest.fixture
def authed_client(client, django_user_model):
    user = django_user_model.objects.create_user(username='testuser', email='test@example.com', password='pass')
    client.login(username='testuser', password='pass')
    return client, user
