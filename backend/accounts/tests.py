"""
Тесты на основе pytest
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.parametrize(
    "field, value",
    [
        ("username", "short"),
        ("password1", "123"),
        ("password2", "123___"),
    ],
)
@pytest.mark.django_db
def test_register(client, field, value):
    """
    Тест проверки регистрации пользователя при неправильных данных.
    Пользователь не создается.
    :param client: fiхtures
    :param field:
    :param value:
    :return: 200
    """

    url = reverse("accounts:registers")
    data = {
        "username": "validuser",
        "password1": "strongpassword123",
        "password2": "verySecure123",
    }

    data[field] = value

    response = client.post(url, data)
    assert response.status_code == 200
    assert "form" in response.context
    assert response.context["form"].errors
    assert not User.objects.filter(username="validuser").exists()


@pytest.mark.django_db
def test_register_success(client):
    """
    Тест успешной регистрации пользователя. Возвращает код 302 (перенаправляет
    на страницу об успешной регистрации)
    :param client: fiхtures
    :return: 302
    """

    url = reverse("accounts:registers")
    data = {
        "username": "newuser",
        "password1": "verySecure123",
        "password2": "verySecure123",
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert User.objects.filter(username="newuser").exists()
    assert "message" in response.url


@pytest.mark.django_db
def test_login(db, client, user):
    """
    Тест проверки входа пользователя. Возвращает код 302 и отправляет на
    главную страницу.
    :param client: fiхtures
    :return: 302
    """

    url = reverse("accounts:login")
    data = {"username": "TestUser", "password": "Test1999"}

    response = client.post(url, data)
    assert response.status_code == 302
    assert response.wsgi_request.user.is_authenticated
    assert "/" in response.url


@pytest.mark.django_db
def test_invalid_password(client):
    """
    Тест проверки входа с ошибочными данными. Пользователь не входит.
    :param client: fiхtures
    :return: 200
    """

    url = reverse("accounts:login")
    data = {"username": "TestUser", "password": "Test"}

    response = client.post(url, data)
    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert response.context["form"].errors
    assert "form" in response.context


def test_logout(client, auth_user):
    """
    Тест проверки выхода. Возвращает код 302 и направляет на страницу входа.
    :param client: fiхtures
    :return: 200
    """

    url = reverse("accounts:logout")
    response = client.get(url)
    assert response.status_code == 302
    assert not response.wsgi_request.user.is_authenticated
    assert "login" in response.url

    response = auth_user.get(url)
    assert response.status_code == 302
    assert not response.wsgi_request.user.is_authenticated
    assert "login" in response.url


def test_error_register(db, client, user):
    """
    Тест попытки повторной регистрации пользователя.
    Пользователь не создан.
    :param client: fiхtures
    :return: 200
    """

    url = reverse("accounts:registers")
    data = {
        "username": "TestUser",
        "password1": "12345test",
        "password2": "12345test",
    }

    response = client.post(url, data)
    assert response.status_code == 200
    assert "form" in response.context
    assert "username" in response.context["form"].errors


def test_login_for_all(client):
    """
    Тест проверки возможности зайти на страницу входа любому пользователю.
    :param client: fiхtures
    :return: 200
    """

    url = reverse("accounts:login")
    response = client.get(url)
    assert response.status_code == 200


def test_home_page(client, auth_user):
    """
    Тест проверки возможности входа на главную страницу.
    :param client: fiхtures
    :return: 302
    """

    response = client.get("/")
    assert response.status_code == 200
    response = auth_user.get("/")
    assert response.status_code == 200
