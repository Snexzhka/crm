import datetime

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import Contract
from products.models import Product
from ads.models import Advert
from leads.models import Lead


@pytest.mark.django_db
def test_model_contract(contract, lead, product):
    assert contract.lead.first_name == "Test"
    assert contract.products.name == "TestProd"
    assert contract.name == "TestContract"
    assert contract.cost == 10000


@pytest.mark.django_db
def test_view_contract(client):
    url = reverse("contracts:contracts-list")
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_view_by_user(auth_user, user):
    url = reverse("contracts:contracts-list")
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Contract)
    permission = Permission.objects.get(content_type=content_type, codename='view_contract')
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_view_by_admin(auth_admin):
    url = reverse("contracts:contracts-list")
    response = auth_admin.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_detail_contract(client, contract):
    url = reverse("contracts:contracts-detail", kwargs={"pk":contract.pk})
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_detail_by_user(auth_user, contract, user):
    url = reverse("contracts:contracts-detail", kwargs={"pk":contract.pk})
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Contract)
    permission = Permission.objects.get(content_type=content_type, codename='view_contract')
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_detail_by_admin(auth_admin, contract):
    url = reverse("contracts:contracts-detail", kwargs={"pk":contract.pk})
    response = auth_admin.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_create_contract(client, contract, product, lead):
    data = {
        "name": "NewContract",
        "cost": 180,
        "products":product.pk,
        "lead":lead.pk,
        "duration":"7 00:00:00",
    }
    url = reverse("contracts:contracts_create")
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_create_by_user(auth_user, user, contract, product, lead):
    product_ct = ContentType.objects.get_for_model(Product)
    lead_ct = ContentType.objects.get_for_model(Lead)
    view_product = Permission.objects.get(content_type=product_ct, codename='view_product')
    view_lead = Permission.objects.get(content_type=lead_ct, codename='view_lead')
    user.user_permissions.add(view_product, view_lead)
    data = {
        "name":"NewContract",
        "cost":180,
        "products":product.pk,
        "lead":lead.pk,
        "duration":"7 00:00:00",
    }
    url = reverse("contracts:contracts_create")
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Contract)
    view_perm = Permission.objects.get(content_type=content_type, codename='view_contract')
    add_perm = Permission.objects.get(content_type=content_type, codename='add_contract')
    user.user_permissions.add(view_perm, add_perm)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Contract.objects.filter(name="NewContract").exists()
    assert Contract.objects.count() == 2
    assert Contract.objects.get(name="NewContract").cost == 180


@pytest.mark.django_db
def test_create_by_admin(auth_admin, contract, product, lead):
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
    data = {
        "name": "UpdContract",
        "cost": 200,
        "products":product.pk,
        "lead":lead.pk,
        "duration":"7 00:00:00",
    }
    url = reverse("contracts:contract-update", kwargs={"pk":contract.pk})
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_update_by_user(auth_user, user, contract, product, lead):
    product_ct = ContentType.objects.get_for_model(Product)
    lead_ct = ContentType.objects.get_for_model(Lead)
    view_product = Permission.objects.get(content_type=product_ct, codename='view_product')
    view_lead = Permission.objects.get(content_type=lead_ct, codename='view_lead')
    user.user_permissions.add(view_product, view_lead)

    data = {
        "name": "UpdContract",
        "cost": 200,
        "products":product.pk,
        "lead":lead.pk,
        "duration":"7 00:00:00",
    }
    url = reverse("contracts:contract-update", kwargs={"pk":contract.pk})
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Contract)
    view_perm = Permission.objects.get(content_type=content_type, codename='view_contract')
    change_perm = Permission.objects.get(content_type=content_type, codename='change_contract')
    user.user_permissions.add(view_perm, change_perm)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Contract.objects.filter(name="UpdContract").exists()
    assert Contract.objects.get(name="UpdContract").cost == 200


@pytest.mark.django_db
def test_update_by_admin(auth_admin, contract, product, lead):

    data = {
        "name": "UpdContract",
        "cost": 200,
        "products":product.pk,
        "lead":lead.pk,
        "duration":"7 00:00:00",
    }
    url = reverse("contracts:contract-update", kwargs={"pk":contract.pk})
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    assert Contract.objects.filter(name="UpdContract").exists()
    assert Contract.objects.get(name="UpdContract").cost == 200


@pytest.mark.django_db
def test_delete_contract(client, contract, product, lead):
    url = reverse("contracts:contract-delete", kwargs={"pk":contract.pk})
    response = client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_user(auth_user, user, contract, product, lead):
    url = reverse("contracts:contract-delete", kwargs={"pk":contract.pk})
    response = auth_user.post(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Contract)
    view_perm = Permission.objects.get(content_type=content_type, codename='view_contract')
    delete_perm = Permission.objects.get(content_type=content_type, codename='delete_contract')
    user.user_permissions.add(view_perm, delete_perm)

    response = auth_user.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_admin(auth_admin, contract, product, lead):
    url = reverse("contracts:contract-delete", kwargs={"pk":contract.pk})
    response = auth_admin.post(url)
    assert response.status_code == 302
    assert not Contract.objects.filter(name="TestContract").exists()
