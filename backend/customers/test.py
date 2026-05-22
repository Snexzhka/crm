from datetime import datetime, timedelta

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import Customer
from leads.models import Lead
from contracts.models import Contract
from products.models import Product
from ads.models import Advert

@pytest.mark.django_db
def test_model_customer(customer, lead, contract):
    """
    Тест проверки создания объектов моделей активных клинтов
    """
    assert customer.contract.name == "TestContract"
    assert customer.lead.first_name == "Test"
    assert customer.contract.cost == 10000
    assert customer.lead.email == "test@test.by"

@pytest.mark.django_db
def test_view_customer(client):
    """
    Тест проверки невозможности просмотра списка клиентов неавторизованным пользователем
    """
    url = reverse("customers:customers-list")
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_view_by_user(auth_user, user):
    """
    Тест проверки возможности просмотра списка клиентов авторизованным пользователем.
    Возможно после получения доп.прав
    """
    url = reverse("customers:customers-list")
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Customer)
    permission = Permission.objects.get(content_type=content_type, codename='view_customer')
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_by_admin(auth_admin):
    """
    Тест проверки возможности просмотра списка клиентов администратором
    :param auth_admin: fixture
    :return: 200
    """
    url = reverse("customers:customers-list")
    response = auth_admin.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_detail_customer(client, customer):
    """
    Тест проверки невозможности просмотра деталей клиентов неавторизованным пользователем
    :param client: fixture
    :param customer: fixture
    :return: 302
    """
    url = reverse("customers:customers-detail", kwargs={"pk":customer.pk})
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_detail_by_user(auth_user, customer, user):
    """
    Тест проверки возможности просмотра деталей клиентов авторизованным пользователем
    :param client: fixture
    :param customer: fixture
    :return: 200
    """
    url = reverse("customers:customers-detail", kwargs={"pk":customer.pk})
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Customer)
    permission = Permission.objects.get(content_type=content_type, codename='view_customer')
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_detail_by_admin(auth_admin, customer, user):
    """
    Тест проверки возможности просмотра деталей клиентов администратором
    :param client: fixture
    :param customer: fixture
    :return: 200
    """
    url = reverse("customers:customers-detail", kwargs={"pk":customer.pk})
    response = auth_admin.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_customer(client, customer, lead, contract, ads, product):
    """
    Тест невозможности создания клиента неавторизованным пользователем.
    Возвращает на страницу входа
    :param client: fixture
    :param customer: fixture
    :param lead: fixture
    :param contract: fixture
    :param ads: fixture
    :param product: fixture
    :return: 302
    """
    new_lead = Lead.objects.create(
        first_name="TestNew",
        last_name="testych",
        phone="+234578",
        email="newtest@test.by",
        advert_name=ads,
    )

    new_contract = Contract.objects.create(
        name="TestContractNew",
        cost=10000,
        products=product,
        lead=lead,
        duration=timedelta(days=5),
    )

    data = {
        "lead":new_lead.pk,
        "contract":new_contract.pk,
    }
    url = reverse("customers:customers-create")
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_create_by_user(auth_user, user, customer, lead, contract, ads, product):
    """
    Тест возможности создания клиента авторизованным пользователем при предоставлении доп.прав.
    :param client: fixture
    :param customer: fixture
    :param lead: fixture
    :param contract: fixture
    :param ads: fixture
    :param product: fixture
    :return: 302
    """
    new_lead = Lead.objects.create(
        first_name="TestNew",
        last_name="testych",
        phone="+234578",
        email="newtest@test.by",
        advert_name=ads,
    )

    new_contract = Contract.objects.create(
        name="TestContractNew",
        cost=10000,
        products=product,
        lead=lead,
        duration=timedelta(days=5),
    )

    data = {
        "lead": new_lead.pk,
        "contract": new_contract.pk,
    }

    url = reverse("customers:customers-create")
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Customer)
    add_permission = Permission.objects.get(content_type=content_type, codename='add_customer')
    view_permission = Permission.objects.get(content_type=content_type, codename='view_customer')
    user.user_permissions.add(view_permission, add_permission)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Customer.objects.count() == 2


@pytest.mark.django_db
def test_create_by_admin(auth_admin, customer, lead, contract, ads, product):
    """
    Тест возможности создания клиента авторизованным пользователем без предоставления доп.прав.
    :param client: fixture
    :param customer: fixture
    :param lead: fixture
    :param contract: fixture
    :param ads: fixture
    :param product: fixture
    :return: 302
    """
    new_lead = Lead.objects.create(
        first_name="TestNew",
        last_name="testych",
        phone="+234578",
        email="newtest@test.by",
        advert_name=ads,
    )

    new_contract = Contract.objects.create(
        name="TestContractNew",
        cost=10000,
        products=product,
        lead=lead,
        duration=timedelta(days=5),
    )

    data = {
        "lead": new_lead.pk,
        "contract": new_contract.pk,
    }

    url = reverse("customers:customers-create")
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    assert Customer.objects.count() == 2


@pytest.mark.django_db
def test_update_customer(client, customer, lead, contract, ads, product):
    """
    Тест невозможности обновления  клиентов неавторизованным пользователем.
    Возвращает 302 и перенаправляет на страницу входа.
    :param client: fixture
    :param customer: fixture
    :param lead: fixture
    :param contract: fixture
    :param ads: fixtureн
    :param product: fixture
    :return: 302
    """
    new_lead = Lead.objects.create(
        first_name="TestUpdate",
        last_name="testych_upd",
        phone="+234578",
        email="test_upd@test.by",
        advert_name=ads,
    )

    new_contract = Contract.objects.create(
        name="TestContractUpdate",
        cost=10000,
        products=product,
        lead=lead,
        duration=timedelta(days=5),
    )

    data = {
        "lead":new_lead.pk,
        "contract":new_contract.pk,
    }
    url = reverse("customers:customer_update", kwargs={"pk":customer.pk})
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_update_by_user(auth_user, user, customer, lead, contract, ads, product):
    """
    Тест возможности обновления клиентов авторизованным пользователем. После получения разрешений
    создает нового клиента и возвращает 302 с перенаправлением на список клиентов.
    :param client: fixture
    :param customer: fixture
    :param lead: fixture
    :param contract: fixture
    :param ads: fixtureн
    :param product: fixture
    :return: 302
    """
    new_lead = Lead.objects.create(
        first_name="TestUpdate",
        last_name="testych_upd",
        phone="+234578",
        email="test_upd@test.by",
        advert_name=ads,
    )

    new_contract = Contract.objects.create(
        name="TestContractUpdate",
        cost=100000,
        products=product,
        lead=lead,
        duration=timedelta(days=5),
    )

    data = {
        "lead":new_lead.pk,
        "contract":new_contract.pk,
    }
    url = reverse("customers:customer_update", kwargs={"pk":customer.pk})
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Customer)
    change_permission = Permission.objects.get(content_type=content_type, codename='change_customer')
    view_permission = Permission.objects.get(content_type=content_type, codename='view_customer')
    user.user_permissions.add(view_permission, change_permission)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    customer.refresh_from_db()
    assert customer.lead.email == "test_upd@test.by"
    assert customer.contract.cost == 100000


@pytest.mark.django_db
def test_update_by_admin(auth_admin, customer, lead, contract, ads, product):
    """
    Тест возможности обновления клиентов администратором.
    Создает нового клиента и возвращает 302 с перенаправлением на список клиентов.
    :param client: fixture
    :param customer: fixture
    :param lead: fixture
    :param contract: fixture
    :param ads: fixtureн
    :param product: fixture
    :return: 302
    """
    new_lead = Lead.objects.create(
        first_name="TestUpdate",
        last_name="testych_upd",
        phone="+234578",
        email="test_upd@test.by",
        advert_name=ads,
    )

    new_contract = Contract.objects.create(
        name="TestContractUpdate",
        cost=100000,
        products=product,
        lead=lead,
        duration=timedelta(days=5),
    )

    data = {
        "lead":new_lead.pk,
        "contract":new_contract.pk,
    }
    url = reverse("customers:customer_update", kwargs={"pk":customer.pk})
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    customer.refresh_from_db()
    assert customer.lead.email == "test_upd@test.by"
    assert customer.contract.cost == 100000


@pytest.mark.django_db
def test_delete_customer(client, customer, lead, contract, ads, product):
    """
    Тест проверки невозможности удаления клиента неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа
    ::param client: fixture
    :param customer: fixture
    :param lead: fixture
    :param contract: fixture
    :param ads: fixture
    :param product: fixture
    :return: 302
    """
    url = reverse("customers:customer-delete", kwargs={"pk":customer.pk})
    response = client.post(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_delete_by_user(auth_user, user, customer, lead, contract, ads, product):
    """
    Тест проверки возможности удаления клиента авторизованным пользователем. После получения разрешений
    удаление невозможно по причине ограничений на удаление.
    ::param client: fixture
    :param customer: fixture
    :param lead: fixture
    :param contract: fixture
    :param ads: fixtureн
    :param product: fixture
    :return: 302
    """
    url = reverse("customers:customer-delete", kwargs={"pk":customer.pk})
    response = auth_user.post(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Customer)
    delete_permission = Permission.objects.get(content_type=content_type, codename='delete_customer')
    view_permission = Permission.objects.get(content_type=content_type, codename='view_customer')
    user.user_permissions.add(view_permission, delete_permission)

    response = auth_user.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_admin(auth_admin, customer, lead, contract, ads, product):
    """
    Тест проверки возможности удаления клиента админом. Удаляет клиента и
    возвращает на страницу деталей клиента.
    ::param client: fixture
    :param customer: fixture
    :param lead: fixture
    :param contract: fixture
    :param ads: fixture
    :param product: fixture
    :return: 302
    """
    url = reverse("customers:customer-delete", kwargs={"pk":customer.pk})
    response = auth_admin.post(url)
    assert response.status_code == 302
    assert not Customer.objects.filter(pk=customer.pk).exists()
    assert Contract.objects.filter(pk=contract.pk).exists()
    assert Lead.objects.filter(pk=lead.pk).exists()
