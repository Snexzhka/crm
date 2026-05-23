"""
Тесты на основе pytest
"""

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from ads.models import Advert
from products.models import Product

from .models import Lead


@pytest.mark.django_db
def test_lead_model(lead, ads):
    """
    Тест проверки создания объектов модели потенциального клиента
    :param lead: fixture
    :param ads: fixture
    """

    assert lead.first_name == "Test"
    assert lead.email == "test@test.by"
    assert lead.phone == "+234578"
    assert lead.last_name == "testych"


@pytest.mark.django_db
def test_view_lead(client):
    """
    Тест невозможности просмотра списка клиентов неавторизованным пользователем.
    Возвращает код 302 и перенаправляет на страницу входа.
    :param client: fixture
    :return: 302
    """

    url = reverse("leads:leads-list")
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_view_by_user(auth_user, user):
    """
    Тест возможности просмотра списка клиентов авторизованным пользователем.
    Возвращает код 200 при предоставлении разрешений.
    :param auth_user: fixture
    :param user: fixture
    :return: 200
    """

    url = reverse("leads:leads-list")
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Lead)
    permission = Permission.objects.get(content_type=content_type, codename="view_lead")
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200
    assert "user" in response.context


@pytest.mark.django_db
def test_view_by_admin(auth_admin):
    """
    Тест возможности просмотра списка клиентов администратором.
    Возвращает код 200.
    :param auth_admin: fixture
    :return: 200
    """

    url = reverse("leads:leads-list")
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert "user" in response.context


@pytest.mark.django_db
def test_detail_lead(client, lead):
    """
    Тест проверки невозможности просмотра деталей клиента неавторизованным
    пользователем. Возвращает код 302 и перенаправляет на страницу входа.
    :param client: fixture
    :param lead: fixture
    :return: 302
    """

    url = reverse("leads:leads-detail", kwargs={"pk": lead.pk})
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_detail_by_user(auth_user, lead, user):
    """
    Тест проверки возможности просмотра деталей клиента авторизованным пользователем.
    Возвращает код 200 при наличии определенных прав.
    :param auth_user: fixture
    :param lead: fixture
    :param user: fixture
    :return: 200
    """

    url = reverse("leads:leads-detail", kwargs={"pk": lead.pk})
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Lead)
    permission = Permission.objects.get(content_type=content_type, codename="view_lead")
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200
    assert Lead.objects.get(first_name="Test").last_name == "testych"


@pytest.mark.django_db
def test_detail_by_admin(auth_admin, lead):
    """
    Тест проверки возможности просмотра деталей клиента администратором.
    Возвращает код 200.
    :param auth_admin: fixture
    :param lead: fixture
    :return: 200
    """

    url = reverse("leads:leads-detail", kwargs={"pk": lead.pk})
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert Lead.objects.get(first_name="Test").last_name == "testych"


@pytest.mark.django_db
def test_create_lead(client, lead, ads):
    """
    Тест проверки невозможности создания клиента неавторизованным
    пользователем. Возвращает код 302 и перенаправляет на страницу входа.
    :param client: fixture
    :param lead: fixture
    :param ads: fixture
    :return: 302
    """

    data = {
        "first_name": "NewTest",
        "last_name": "testych_new",
        "phone": "+234578",
        "email": "newtest@test.by",
        "advert_name": ads.pk,
    }
    url = reverse("leads:leads-create")
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_create_by_user(auth_user, lead, user, ads):
    """
    Тест проверки возможности создания клиента авторизованным пользователем.
    Возвращает код 302 и создает клиента при наличии определенных прав.
    :param auth_user: fixture
    :param lead: fixture
    :param user: fixture
    :param ads: fixture
    :return: 302
    """

    product_ct = ContentType.objects.get_for_model(Product)
    view_product = Permission.objects.get(
        content_type=product_ct, codename="view_product"
    )
    advert_ct = ContentType.objects.get_for_model(Advert)
    view_advert = Permission.objects.get(content_type=advert_ct, codename="view_advert")
    user.user_permissions.add(view_product, view_advert)

    data = {
        "first_name": "NewTest",
        "last_name": "testych_new",
        "phone": "+234578",
        "email": "newtest@test.by",
        "advert_name": ads.pk,
    }
    url = reverse("leads:leads-create")
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Lead)
    view_permission = Permission.objects.get(
        content_type=content_type, codename="view_lead"
    )
    add_permission = Permission.objects.get(
        content_type=content_type, codename="add_lead"
    )
    user.user_permissions.add(view_permission, add_permission)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Lead.objects.count() == 2
    assert Lead.objects.filter(first_name="NewTest").exists()
    assert Lead.objects.get(first_name="NewTest").last_name == "testych_new"


@pytest.mark.django_db
def test_create_by_admin(auth_admin, lead, ads):
    """
    Тест проверки возможности создания клиента администратором.
    Возвращает код 302 и перенаправляет на страницу списка клиентов.
    :param auth_admin: fixture
    :param lead: fixture
    :param ads: fixture
    :return: 302
    """

    data = {
        "first_name": "NewTest",
        "last_name": "testych_new",
        "phone": "+234578",
        "email": "newtest@test.by",
        "advert_name": ads.pk,
    }
    url = reverse("leads:leads-create")
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    assert Lead.objects.count() == 2
    assert Lead.objects.filter(first_name="NewTest").exists()
    assert Lead.objects.get(first_name="NewTest").last_name == "testych_new"


@pytest.mark.django_db
def test_update_lead(client, lead, ads):
    """
    Тест проверки невозможности обновления клиента неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param client: fixture
    :param lead: fixture
    :param ads: fixture
    :return: 302
    """

    data = {
        "first_name": "UpdateTest",
        "last_name": "testych_upd",
        "phone": "+234578",
        "email": "newtest@test.by",
        "advert_name": ads.pk,
    }
    url = reverse("leads:leads-update", kwargs={"pk": lead.pk})
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_update_by_user(auth_user, lead, ads, user):
    """
    Тест проверки возможности обновления клиента авторизованным пользователем.
    Возвращает код 302 и направляет на страницу деталей клиента
    при наличии определенных прав.
    :param auth_user: fixture
    :param lead: fixture
    :param ads: fixture
    :param user: fixture
    :return: 302
    """

    product_ct = ContentType.objects.get_for_model(Product)
    view_product = Permission.objects.get(
        content_type=product_ct, codename="view_product"
    )
    advert_ct = ContentType.objects.get_for_model(Advert)
    view_advert = Permission.objects.get(content_type=advert_ct, codename="view_advert")
    user.user_permissions.add(view_product, view_advert)

    data = {
        "first_name": "UpdateTest",
        "last_name": "testych_upd",
        "phone": "+234578",
        "email": "newtest@test.by",
        "advert_name": ads.pk,
    }
    url = reverse("leads:leads-update", kwargs={"pk": lead.pk})
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Lead)
    view_permission = Permission.objects.get(
        content_type=content_type, codename="view_lead"
    )
    change_permission = Permission.objects.get(
        content_type=content_type, codename="change_lead"
    )
    user.user_permissions.add(view_permission, change_permission)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Lead.objects.filter(first_name="UpdateTest").exists()
    assert Lead.objects.get(first_name="UpdateTest").email == "newtest@test.by"


@pytest.mark.django_db
def test_update_by_admin(auth_admin, lead, ads, user):
    """
    Тест проверки возможности обновления клиента администратором.
    Возвращает код 302 и направляет на страницу деталей клиента.
    :param auth_admin: fixture
    :param lead: fixture
    :param ads: fixture
    :param user: fixture
    :return: 302
    """

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
    """
    Тест проверки невозможности удаления клиента неавторизованным пользователем.
    Возвращает код 403.
    :param client: fixture
    :param lead: fixture
    :return: 403
    """

    url = reverse("leads:leads-delete", kwargs={"pk": lead.pk})
    response = client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_user(auth_user, lead, user):
    """
    Тест проверки невозможности удаления клиента авторизованным пользователем.
    Возвращает код 403 даже при наличии определенных прав (такое удаление заложено
    в представлении)
    :param auth_user: fixture
    :param lead: fixture
    :param user: fixture
    :return: 403
    """

    product_ct = ContentType.objects.get_for_model(Product)
    view_product = Permission.objects.get(
        content_type=product_ct, codename="view_product"
    )
    advert_ct = ContentType.objects.get_for_model(Advert)
    view_advert = Permission.objects.get(content_type=advert_ct, codename="view_advert")
    user.user_permissions.add(view_product, view_advert)

    url = reverse("leads:leads-delete", kwargs={"pk": lead.pk})
    response = auth_user.post(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Lead)
    view_permission = Permission.objects.get(
        content_type=content_type, codename="view_lead"
    )
    delete_permission = Permission.objects.get(
        content_type=content_type, codename="delete_lead"
    )
    user.user_permissions.add(view_permission, delete_permission)

    response = auth_user.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_admin(auth_admin, lead):
    """
    Тест проверки возможности удаления клиента администратором.
    Возвращает код 302 и направляет на страницу списка клиентов.
    :param auth_admin: fixture
    :param lead: fixture
    :return: 302
    """

    url = reverse("leads:leads-delete", kwargs={"pk": lead.pk})
    response = auth_admin.post(url)
    assert response.status_code == 302
    assert not Lead.objects.filter(first_name="Test").exists()
