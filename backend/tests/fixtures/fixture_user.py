import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token


@pytest.fixture
def admin(django_user_model):
    return django_user_model.objects.create_user(
        username='TestAdmin',
        email='testadmin@yamdb.fake',
        firstname='AdminFirstName',
        last_name='AdminLastName',
        password='12345678',
        is_staff=True,
    )


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser',
        email='testuser@yamdb.fake',
        firstname='UserFirstName',
        last_name='UserLastName',
        password='12345678',
        is_staff=False,
    )


@pytest.fixture
def token_admin(admin):
    token = Token.for_user(admin)
    return {
        'access': str(token),
    }


@pytest.fixture
def admin_client(token_admin):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_admin["access"]}')
    return client


@pytest.fixture
def token_user(user):
    token = Token.for_user(user)
    return {
        'access': str(token),
    }


@pytest.fixture
def user_client(token_user):
    client = APIClient()
    client.credentials(HTTP_AUTHORIZATION=f'Token {token_user["access"]}')
    return client
