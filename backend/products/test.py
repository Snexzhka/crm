import pytest
import rest_framework.urls
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import Product

@pytest.mark.django_db
def test_product_model(product):
    """
    Тест проверки создания моделей услуг
    :param product: fixture
    """
    assert product.name == "TestProd"
    assert product.cost == 100


@pytest.mark.django_db
def test_view_product(client, user):
    """
    Тест проверки невозможности просмотра списка услуг неавторизованным пользователем.
    Возвращает код 302 и перенаправляет на страницу входа.
    :param client: fixture
    :param user: fixture
    :return: 302
    """
    url = reverse("products:product-list")
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_view_by_user(auth_user, user):
    """
    Тест проверки возможности просмотра списка услуг авторизованным пользователем.
    Возвращает код 200 при наличии определенных разрешений.
    :param client: fixture
    :param user: fixture
    :return: 200
    """
    url = reverse("products:product-list")
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Product)
    permission = Permission.objects.get(content_type=content_type, codename='view_product')
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200
    assert "products" in response.context


@pytest.mark.django_db
def test_view_by_admin(auth_admin):
    """
    Тест проверки возможности просмотра списка услуг администратором.
    Возвращает код 200.
    :param client: fixture
    :param user: fixture
    :return: 200
    """
    url = reverse("products:product-list")
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert "products" in response.context


@pytest.mark.django_db
def test_view_detail_product(client, user, product):
    """
    Тест проверки невозможности просмотра деталей услуг неавторизованным пользователем.
    Возвращает код 302 и перенаправляет на страницу входа.
    :param client: fixture
    :param user: fixture
    :return: 302
    """
    url = reverse("products:product-detail", kwargs={"pk":product.pk})
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_view_detail_by_user(auth_user, user, product):
    """
    Тест проверки возможности просмотра деталей услуг авторизованным пользователем.
    Возвращает код 200 при наличии определенных разрешений.
    :param client: fixture
    :param user: fixture
    :return: 200
    """
    url = reverse("products:product-detail", kwargs={"pk": product.pk})
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Product)
    permission = Permission.objects.get(content_type=content_type, codename='view_product')
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200
    assert "user" in response.context


@pytest.mark.django_db
def test_view_detail_by_admin(auth_admin, product):
    """
    Тест проверки возможности просмотра деталей  услуг администратором.
    Возвращает код 200.
    :param client: fixture
    :param user: fixture
    :return: 200
    """
    url = reverse("products:product-detail", kwargs={"pk": product.pk})
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert Product.objects.count() == 1


@pytest.mark.django_db
def test_create_product(client, product):
    """
    Тест проверки невозможности создания услуги неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param client: fixture
    :param product: fixture
    :return: 302
    """
    url = reverse("products:product-create")
    data = {
        "name":"NewProd",
        "description":"NewDesc",
        "cost":2000,
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_create_by_user(user, auth_user, product):
    """
    Тест проверки возможности создания услуги авторизованным пользователем.
    Возвращает код 302 и создает услугу при наличии определенных прав.
    :param client: fixture
    :param product: fixture
    :return: 302
    """
    url = reverse("products:product-create")
    data = {
        "name": "NewProd",
        "description": "NewDesc",
        "cost": 2000,
    }
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Product)
    view_permission = Permission.objects.get(content_type=content_type, codename='view_product')
    add_permission = Permission.objects.get(content_type=content_type, codename='add_product')
    user.user_permissions.add(view_permission, add_permission)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Product.objects.filter(name="NewProd").exists()
    assert Product.objects.count() == 2


@pytest.mark.django_db
def test_create_by_admin(auth_admin, product):
    """
    Тест проверки возможности создания услуги администратором.
    Возвращает код 302 и создает услугу.
    :param client: fixture
    :param product: fixture
    :return: 302
    """
    url = reverse("products:product-create")
    data = {
        "name": "NewProd",
        "description": "NewDesc",
        "cost": 2000,
    }
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    assert Product.objects.filter(name="NewProd").exists()
    assert Product.objects.count() == 2
    new_prod = Product.objects.get(name="NewProd")
    assert new_prod.cost == 2000
    assert Product.objects.count() == 2


@pytest.mark.django_db
def test_update_product(client, product):
    """
    Тест проверки невозможности обновления услуги неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param client: fixture
    :param product: fixture
    :return: 302
    """
    data = {
        "name": "UpdateProd",
        "description": "UpdateDesc",
        "cost": 8000,
    }
    url = reverse("products:product-update", kwargs={"pk":product.pk})
    response = client.post(url,data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_update_by_user(user, auth_user, product):
    """
    Тест проверки возможности обновления услуги авторизованным пользователем.
    Возвращает код 302 и обновляет услугу при наличии определенных прав.
    :param client: fixture
    :param product: fixture
    :return: 302
    """
    data = {
        "name": "UpdateProd",
        "description": "UpdateDesc",
        "cost": 8000,
    }
    url = reverse("products:product-update", kwargs={"pk": product.pk})
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Product)
    view_permission = Permission.objects.get(content_type=content_type, codename='view_product')
    change_permission = Permission.objects.get(content_type=content_type, codename='change_product')
    user.user_permissions.add(view_permission, change_permission)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Product.objects.filter(name="UpdateProd").exists()
    upd_prod = Product.objects.get(name="UpdateProd")
    assert upd_prod.cost == 8000


@pytest.mark.django_db
def test_update_by_admin(auth_admin, product):
    """
    Тест проверки возможности обновления услуги администратором.
    Возвращает код 302 и обновляет поля услуги.
    :param client: fixture
    :param product: fixture
    :return: 302
    """
    data = {
        "name": "UpdateProd",
        "description": "UpdateDesc",
        "cost": 8000,
    }
    url = reverse("products:product-update", kwargs={"pk": product.pk})
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    assert Product.objects.filter(name="UpdateProd").exists()
    upd_prod = Product.objects.get(name="UpdateProd")
    assert upd_prod.cost == 8000

@pytest.mark.django_db
def test_delete_products(client, product):
    """
    Тест проверки невозможности удаления услуги неавторизованным пользователем.
    Возвращает код 403.
    :param client: fixture
    :param product: fixture
    :return: 403
    """
    url = reverse("products:product-delete", kwargs={"pk":product.pk})
    response = client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_user(user, auth_user, product):
    """
    Тест проверки невозможности удаления услуги авторизованным пользователем.
    Возвращает код 403 даже при наличии прав.
    :param client: fixture
    :param product: fixture
    :return: 403
    """
    url = reverse("products:product-delete", kwargs={"pk":product.pk})
    response = auth_user.post(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Product)
    view_permission = Permission.objects.get(content_type=content_type, codename='view_product')
    delete_permission = Permission.objects.get(content_type=content_type, codename='delete_product')
    user.user_permissions.add(view_permission, delete_permission)

    response = auth_user.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_admin(auth_admin, product):
    """
    Тест проверки возможности удаления услуги администратором.
    Возвращает код 302 и направляет на страницу списка услуг.
    :param client: fixture
    :param product: fixture
    :return: 302
    """
    url = reverse("products:product-delete", kwargs={"pk":product.pk})
    response = auth_admin.post(url)
    assert response.status_code == 302
    assert not Product.objects.filter(name="TestProd").exists()
    assert Product.objects.count() == 0
