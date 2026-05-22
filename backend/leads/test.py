import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import Lead
from ads.models import Advert
from products.models import Product

@pytest.mark.django_db
def test_lead_model(lead, ads):
    assert lead.first_name == "Test"
    assert lead.email == "test@test.by"
    assert lead.phone == "+234578"
    assert lead.last_name == "testych"


@pytest.mark.django_db
def test_view_lead(client):
    url = reverse("leads:leads-list")
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_view_by_user(auth_user, user):
    url = reverse("leads:leads-list")
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Lead)
    permission = Permission.objects.get(content_type=content_type, codename='view_lead')
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200
    assert "user" in response.context


@pytest.mark.django_db
def test_view_by_admin(auth_admin):
    url = reverse("leads:leads-list")
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert "user" in response.context


@pytest.mark.django_db
def test_detail_lead(client, lead):
    url = reverse("leads:leads-detail", kwargs={"pk":lead.pk})
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_detail_by_user(auth_user, lead, user):
    url = reverse("leads:leads-detail", kwargs={"pk": lead.pk})
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Lead)
    permission = Permission.objects.get(content_type=content_type, codename='view_lead')
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200
    assert Lead.objects.get(first_name="Test").last_name == "testych"


@pytest.mark.django_db
def test_detail_by_admin(auth_admin, lead):
    url = reverse("leads:leads-detail", kwargs={"pk": lead.pk})
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert Lead.objects.get(first_name="Test").last_name == "testych"


@pytest.mark.django_db
def test_create_lead(client, lead, ads):
    data = {
        "first_name":"NewTest",
        "last_name":"testych_new",
        "phone":"+234578",
        "email":"newtest@test.by",
        "advert_name":ads.pk,
    }
    url = reverse("leads:leads-create")
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_create_by_user(auth_user, lead, user, ads):
    product_ct = ContentType.objects.get_for_model(Product)
    view_product = Permission.objects.get(content_type=product_ct, codename='view_product')
    advert_ct = ContentType.objects.get_for_model(Advert)
    view_advert = Permission.objects.get(content_type=advert_ct, codename='view_advert')
    user.user_permissions.add(view_product, view_advert)

    data = {
        "first_name":"NewTest",
        "last_name":"testych_new",
        "phone":"+234578",
        "email":"newtest@test.by",
        "advert_name":ads.pk,
    }
    url = reverse("leads:leads-create")
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Lead)
    view_permission = Permission.objects.get(content_type=content_type, codename='view_lead')
    add_permission = Permission.objects.get(content_type=content_type, codename='add_lead')
    user.user_permissions.add(view_permission, add_permission)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Lead.objects.count() == 2
    assert Lead.objects.filter(first_name="NewTest").exists()
    assert Lead.objects.get(first_name="NewTest").last_name == "testych_new"


@pytest.mark.django_db
def test_create_by_admin(auth_admin, lead, ads):
    data = {
        "first_name":"NewTest",
        "last_name":"testych_new",
        "phone":"+234578",
        "email":"newtest@test.by",
        "advert_name":ads.pk,
    }
    url = reverse("leads:leads-create")
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    assert Lead.objects.count() == 2
    assert Lead.objects.filter(first_name="NewTest").exists()
    assert Lead.objects.get(first_name="NewTest").last_name == "testych_new"


@pytest.mark.django_db
def test_update_lead(client, lead, ads):
    data = {
        "first_name":"UpdateTest",
        "last_name":"testych_upd",
        "phone":"+234578",
        "email":"newtest@test.by",
        "advert_name":ads.pk,
    }
    url = reverse("leads:leads-update", kwargs={"pk":lead.pk})
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_update_by_user(auth_user, lead, ads, user):
    product_ct = ContentType.objects.get_for_model(Product)
    view_product = Permission.objects.get(content_type=product_ct, codename='view_product')
    advert_ct = ContentType.objects.get_for_model(Advert)
    view_advert = Permission.objects.get(content_type=advert_ct, codename='view_advert')
    user.user_permissions.add(view_product, view_advert)

    data = {
        "first_name":"UpdateTest",
        "last_name":"testych_upd",
        "phone":"+234578",
        "email":"newtest@test.by",
        "advert_name":ads.pk,
    }
    url = reverse("leads:leads-update", kwargs={"pk":lead.pk})
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Lead)
    view_permission = Permission.objects.get(content_type=content_type, codename='view_lead')
    change_permission = Permission.objects.get(content_type=content_type, codename='change_lead')
    user.user_permissions.add(view_permission, change_permission)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Lead.objects.filter(first_name="UpdateTest").exists()
    assert Lead.objects.get(first_name="UpdateTest").email == "newtest@test.by"


@pytest.mark.django_db
def test_update_by_admin(auth_admin, lead, ads, user):

    data = {
        "first_name": "UpdateTest",
        "last_name": "testych_upd",
        "phone": "+234578",
        "email": "newtest@test.by",
        "advert_name": ads.pk,
    }
    url = reverse("leads:leads-update", kwargs={"pk": lead.pk})
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    assert Lead.objects.filter(first_name="UpdateTest").exists()
    assert Lead.objects.get(first_name="UpdateTest").email == "newtest@test.by"



@pytest.mark.django_db
def test_delete_lead(client, lead):
    url = reverse("leads:leads-delete", kwargs={"pk":lead.pk})
    response = client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_user(auth_user, lead, user):
    product_ct = ContentType.objects.get_for_model(Product)
    view_product = Permission.objects.get(content_type=product_ct, codename='view_product')
    advert_ct = ContentType.objects.get_for_model(Advert)
    view_advert = Permission.objects.get(content_type=advert_ct, codename='view_advert')
    user.user_permissions.add(view_product, view_advert)

    url = reverse("leads:leads-delete", kwargs={"pk": lead.pk})
    response = auth_user.post(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Lead)
    view_permission = Permission.objects.get(content_type=content_type, codename='view_lead')
    delete_permission = Permission.objects.get(content_type=content_type, codename='delete_lead')
    user.user_permissions.add(view_permission, delete_permission)

    response = auth_user.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_admin(auth_admin, lead):
    url = reverse("leads:leads-delete", kwargs={"pk": lead.pk})
    response = auth_admin.post(url)
    assert response.status_code == 302
    assert not Lead.objects.filter(first_name="Test").exists()
