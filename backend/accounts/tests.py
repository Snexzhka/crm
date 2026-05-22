from django.contrib.auth.models import User
from django.test import TestCase
import pytest, pytest_django
from django.urls import reverse


# @pytest.mark.django_db
# def test_product_create(product):
#     assert product.name == "TestProd"


@pytest.mark.parametrize("field, value", [
    ('username', 'short'),
    ('password1', '123'),
    ('password2', '123___'),

])
@pytest.mark.django_db
def test_register(client, field, value):
    url = reverse("accounts:registers")
    data = {
        'username': 'validuser',
        'password1': 'strongpassword123',
        'password2': 'verySecure123'
    }

    data[field] = value

    response = client.post(url, data)
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context['form'].errors
    assert not User.objects.filter(username="validuser").exists()


@pytest.mark.django_db
def test_register_success(client):
    url = reverse('accounts:registers')
    data = {
        'username': 'newuser',
        'password1': 'verySecure123',
        'password2': 'verySecure123',
    }
    response = client.post(url, data)
    # Должен быть редирект (обычно на страницу логина или главную)
    assert response.status_code == 302
    # Проверяем, что пользователь создан
    assert User.objects.filter(username='newuser').exists()


@pytest.mark.django_db
def test_login(client, user):
    url = reverse("accounts:login")
    data = {'username': 'TestUser', 'password': 'Test1999'}

    response = client.post(url, data)
    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated


@pytest.mark.django_db
def test_invalid_password(client, user):
    url = reverse("accounts:login")
    data = {'username': 'TestUser', 'password': 'Test'}

    response = client.post(url, data)
    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert response.context['form'].errors
    assert 'form' in response.context

def test_logout(client, user):
    url = reverse("accounts:login")
    response = client.get(url)
    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated


def test_error_register(client, user):
    url = reverse('accounts:registers')
    data = {
        'username': 'TestUser',
        'password1': '12345test',
        'password2': '12345test',
    }

    response = client.post(url, data)
    assert response.status_code == 200
    assert 'form' in response.context
    assert 'username' in response.context['form'].errors

def test_login_for_all(client):
    url = reverse("accounts:login")
    response = client.get(url)
    assert response.status_code == 200


def test_home_page(client):
    response = client.get("/")
    assert response.status_code == 302