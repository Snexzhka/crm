"""
Тесты на основе pytest
"""

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from leads.models import Lead
from products.models import Product
from .models import Contract


@pytest.mark.django_db
def test_model_contract(contract):
    """
    Тест проверки создания объектов моделей контрактов.
    :param contract: fixtures
    """

    assert contract.lead.first_name == "Test"
    assert contract.products.name == "TestProd"
    assert contract.name == "TestContract"
    assert contract.cost == 10000


@pytest.mark.django_db
def test_view_contract(client):
    """
    Тест проверки невозможности просмотра списка контрактов неавторизованным пользователем.
    Возвращает код 302 и перенаправляет на страницу входа.
    :param client: fixtures
    :return: 302
    """

    url = reverse("contracts:contracts-list")
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_view_by_user(auth_user, user):
    """
    Тест проверки возможности просмотра списка контрактов авторизованным пользователем.
    Возвращает код 200 при наличии определенных разрешений.
    :param user: fixtures
    param auth_user: fixtures
    :return: 200
    """

    url = reverse("contracts:contracts-list")
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Contract)
    permission = Permission.objects.get(
        content_type=content_type, codename="view_contract"
    )
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_by_admin(auth_admin):
    """
    Тест проверки возможности просмотра списка контрактов администратором.
    Возвращает код 200.
    :param auth_admin: fixtures
    :return: 200
    """

    url = reverse("contracts:contracts-list")
    response = auth_admin.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_detail_contract(client, contract):
    """
    Тест проверки невозможности просмотра деталей контрактов неавторизованным пользователем.
    Возвращает код 302 и перенаправляет на страницу входа.
    :param client: fixtures
    :return: 302
    """

    url = reverse("contracts:contracts-detail", kwargs={"pk": contract.pk})
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_detail_by_user(auth_user, contract, user):
    """
    Тест проверки возможности просмотра деталей контрактов авторизованным пользователем.
    Возвращает код 200 при наличии определенных разрешений.
    :param contract: fixtures
    param user: fixtures
    param auth_user: fixtures
    :return: 200
    """

    url = reverse("contracts:contracts-detail", kwargs={"pk": contract.pk})
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Contract)
    permission = Permission.objects.get(
        content_type=content_type, codename="view_contract"
    )
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_detail_by_admin(auth_admin, contract):
    """
    Тест проверки возможности просмотра деталей контрактов администратором.
    Возвращает код 200.
    :param contract: fixtures
    param auth_admin: fixtures
    :return: 200
    """
    url = reverse("contracts:contracts-detail", kwargs={"pk": contract.pk})
    response = auth_admin.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_contract(client, product, lead):
    """
    Тест проверки невозможности создания контракта неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param client: fixtures
    :param product: fixtures
    :param lead: fixtures
    :return: 302
    """

    data = {
        "name": "NewContract",
        "cost": 180,
        "products": product.pk,
        "lead": lead.pk,
        "duration": "7 00:00:00",
    }
    url = reverse("contracts:contracts_create")
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_create_by_user(auth_user, user, product, lead):
    """
    Тест проверки возможности создания контракта авторизованным пользователем.
    Возвращает код 302, создает контракт и направляет на страницу списка контрактов
    при наличии определенных прав.
    :param product: fixtures
    :param lead: fixtures
    param user: fixtures
    param auth_user: fixtures
    :return: 302
    """

    product_ct = ContentType.objects.get_for_model(Product)
    lead_ct = ContentType.objects.get_for_model(Lead)
    view_product = Permission.objects.get(
        content_type=product_ct, codename="view_product"
    )
    view_lead = Permission.objects.get(content_type=lead_ct, codename="view_lead")
    user.user_permissions.add(view_product, view_lead)

    data = {
        "name": "NewContract",
        "cost": 180,
        "products": product.pk,
        "lead": lead.pk,
        "duration": "7 00:00:00",
    }
    url = reverse("contracts:contracts_create")
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Contract)
    view_perm = Permission.objects.get(
        content_type=content_type, codename="view_contract"
    )
    add_perm = Permission.objects.get(
        content_type=content_type, codename="add_contract"
    )
    user.user_permissions.add(view_perm, add_perm)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Contract.objects.filter(name="NewContract").exists()
    assert Contract.objects.count() == 2
    assert Contract.objects.get(name="NewContract").cost == 180


@pytest.mark.django_db
def test_create_by_admin(auth_admin, product, lead):
    """
    Тест проверки возможности создания контракта администратором.
    Возвращает код 302, создает контракт и направляет на страницу списка контрактов.
    :param auth_admin: fixtures
    :param product: fixtures
    :param lead: fixtures
    :return: 302
    """

    data = {
        "name": "NewContract",
        "cost": 180,
        "products": product.pk,
        "lead": lead.pk,
        "duration": "7 00:00:00",
    }
    url = reverse("contracts:contracts_create")
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    assert Contract.objects.filter(name="NewContract").exists()
    assert Contract.objects.count() == 2
    assert Contract.objects.get(name="NewContract").cost == 180


@pytest.mark.django_db
def test_update_contract(client, contract, product, lead):
    """
    Тест проверки невозможности обновления контракта неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param client: fixtures
    :param contract: fixtures
    :param product: fixtures
    :param lead: fixtures
    :return: 302
    """

    data = {
        "name": "UpdContract",
        "cost": 200,
        "products": product.pk,
        "lead": lead.pk,
        "duration": "7 00:00:00",
    }
    url = reverse("contracts:contract-update", kwargs={"pk": contract.pk})
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_update_by_user(auth_user, user, contract, product, lead):
    """
    Тест проверки возможности обновления контракта авторизованным пользователем.
    Возвращает код 302, обновляет контракт и направляет на страницу списка контрактов
    при наличии определенных прав.
    :param auth_user: fixtures
    :param contract: fixtures
    :param product: fixtures
    :param lead: fixtures
    param user: fixtures
    :return: 302
    """

    product_ct = ContentType.objects.get_for_model(Product)
    lead_ct = ContentType.objects.get_for_model(Lead)
    view_product = Permission.objects.get(
        content_type=product_ct, codename="view_product"
    )
    view_lead = Permission.objects.get(content_type=lead_ct, codename="view_lead")
    user.user_permissions.add(view_product, view_lead)

    data = {
        "name": "UpdContract",
        "cost": 200,
        "products": product.pk,
        "lead": lead.pk,
        "duration": "7 00:00:00",
    }
    url = reverse("contracts:contract-update", kwargs={"pk": contract.pk})
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Contract)
    view_perm = Permission.objects.get(
        content_type=content_type, codename="view_contract"
    )
    change_perm = Permission.objects.get(
        content_type=content_type, codename="change_contract"
    )
    user.user_permissions.add(view_perm, change_perm)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Contract.objects.filter(name="UpdContract").exists()
    assert Contract.objects.get(name="UpdContract").cost == 200


@pytest.mark.django_db
def test_update_by_admin(auth_admin, contract, product, lead):
    """
    Тест проверки возможности обновления контракта администратором.
    Возвращает код 302, обновляет контракт и направляет на страницу списка контрактов.
    :param auth_admin: fixtures
    :param contract: fixtures
    :param product: fixtures
    :param lead: fixtures
    :return: 302
    """

    data = {
        "name": "UpdContract",
        "cost": 200,
        "products": product.pk,
        "lead": lead.pk,
        "duration": "7 00:00:00",
    }
    url = reverse("contracts:contract-update", kwargs={"pk": contract.pk})
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    assert Contract.objects.filter(name="UpdContract").exists()
    assert Contract.objects.get(name="UpdContract").cost == 200


@pytest.mark.django_db
def test_delete_contract(client, contract):
    """
    Тест проверки невозможности удаления контракта неавторизованным пользователем.
    Возвращает код 403.
    :param client: fixtures
    :param contract: fixtures
    :return: 403
    """

    url = reverse("contracts:contract-delete", kwargs={"pk": contract.pk})
    response = client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_user(auth_user, user, contract):
    """
    Тест проверки невозможности удаления контракта авторизованным пользователем.
    Возвращает код 403 даже при наличии разрешений (что заложено в представлении).
    :param auth_user: fixtures
    :param contract: fixtures
    param user: fixtures
    :return: 403
    """

    url = reverse("contracts:contract-delete", kwargs={"pk": contract.pk})
    response = auth_user.post(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Contract)
    view_perm = Permission.objects.get(
        content_type=content_type, codename="view_contract"
    )
    delete_perm = Permission.objects.get(
        content_type=content_type, codename="delete_contract"
    )
    user.user_permissions.add(view_perm, delete_perm)

    response = auth_user.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_admin(auth_admin, contract):
    """
    Тест проверки возможности удаления контракта администратором.
    Возвращает код 302 и перенаправляет на страницу списка контрактов
    после удаления объекта.
    :param auth_admin: fixtures
    :param contract: fixtures
    :return: 302
    """

    url = reverse("contracts:contract-delete", kwargs={"pk": contract.pk})
    response = auth_admin.post(url)
    assert response.status_code == 302
    assert not Contract.objects.filter(name="TestContract").exists()
