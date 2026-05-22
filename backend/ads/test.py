import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import Advert


@pytest.mark.django_db
def test_product_create(ads):
    """
    Тест проверки создания моделей рекламной компании
    :param ads: fixture
    """
    assert ads.name == "TestAdvert"
    assert ads.budget == 150


@pytest.mark.django_db
def test_view_by_user(user, auth_user, ads):
    """
    Тест проверки возможности просмотра списка рекламы авторизованным пользователем.
    Возвращает код 200 при наличии разрешений.
    :param user:
    :param auth_user: fixture
    :param ads: fixture
    :return: 200
    """
    url = reverse("ads:ads-list")
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Advert)
    permission = Permission.objects.get(content_type=content_type, codename='view_advert')
    user.user_permissions.add(permission)

    response = auth_user.get(url)
    assert response.status_code == 200
    assert "ads" in response.context
    assert ads.budget == 150


@pytest.mark.django_db
def test_view_by_admin(auth_admin):
    """
    Тест проверки возможности просмотра списка рекламы администратором.
    Возвращает код 200.
    :param user:
    :param auth_user: fixture
    :param ads: fixture
    :return: 200
    """
    url = reverse("ads:ads-list")
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert "user" in response.context
    assert len(response.context) == 2


@pytest.mark.django_db
def test_view(client, user):
    """
    Тест проверки невозможности просмотра списка рекламы неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param user:
    :param auth_user: fixture
    :param ads: fixture
    :return: 302
    """
    url = reverse("ads:ads-list")
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url

@pytest.mark.django_db
def test_view_detail(client, user, ads):
    """
    Тест проверки невозможности просмотра деталей рекламы неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param user:
    :param auth_user: fixture
    :param ads: fixture
    :return: 302
    """
    url = reverse("ads:ads-detail", kwargs={"pk":ads.pk})
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_detail_by_user(auth_user, ads, user):
    """
    Тест проверки возможности просмотра деталей рекламы авторизованным пользователем.
    Возвращает код 200 при наличии разрешений.
    :param user:
    :param auth_user: fixture
    :param ads: fixture
    :return: 200
    """
    url = reverse("ads:ads-detail", kwargs={"pk": ads.pk})
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Advert)
    view_permission = Permission.objects.get(content_type=content_type, codename='view_advert')
    user.user_permissions.add(view_permission)

    response = auth_user.get(url)
    assert response.status_code == 200
    assert ads.name == "TestAdvert"
    assert Advert.objects.count() == 1


@pytest.mark.django_db
def test_detail_by_admin(auth_admin, ads):
    """
    Тест проверки возможности просмотра деталей рекламы администратором.
    Возвращает код 200.
    :param user:  fixture
    :param auth_user: fixture
    :param ads: fixture
    :return: 200
    """
    url = reverse("ads:ads-detail", kwargs={"pk": ads.pk})
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert Advert.objects.count() == 1
    assert ads.budget == 150


@pytest.mark.django_db
def test_create_ads(client, ads, product):
    """
    Тест проверки невозможности создания рекламной компании неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param client:  fixture
    :param ads:  fixture
    :param product:  fixture
    :return: 302
    """
    data = {
        "name": "Advert_new",
        "budget": 22,
        "promotion_path": "news",
        "products":product,
    }
    url = reverse("ads:ads-create")
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_create_by_user(ads, auth_user, product, user):
    """
    Тест проверки возможности создания рекламной компании авторизованным пользователем.
    Возвращает код 302, создает рекламную компанию и направляет на страницу списка рекламы
    при наличии определенных разрешений.
    :param client:  fixture
    :param ads:  fixture
    :param product:  fixture
    :return: 302
    """
    data = {
        "name": "Advert_new",
        "budget": 22,
        "promotion_path": "news",
        "products": product.pk,
    }

    url = reverse("ads:ads-create")
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Advert)
    view_permission = Permission.objects.get(content_type=content_type, codename='view_advert')
    add_permission = Permission.objects.get(content_type=content_type, codename='add_advert')
    user.user_permissions.add(view_permission, add_permission)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Advert.objects.count() == 2
    assert Advert.objects.filter(name="Advert_new").exists()


@pytest.mark.django_db
def test_create_by_admin(auth_admin, product, ads):
    """
    Тест проверки возможности создания рекламной компании администратором.
    Возвращает код 302, создает рекламную компанию и направляет на страницу списка рекламы.
    :param client:  fixture
    :param ads:  fixture
    :param product:  fixture
    :return: 302
    """
    data = {
        "name": "Advert_new",
        "budget": 22,
        "promotion_path": "news",
        "products": product.pk,
    }

    url = reverse("ads:ads-create")
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    assert Advert.objects.count() == 2
    assert Advert.objects.filter(name="Advert_new").exists()


@pytest.mark.django_db
def test_update_advert(client, user, product, ads):
    """
    Тест проверки невозможности обновления рекламной компании неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param client:  fixture
    :param ads:  fixture
    :param product:  fixture
    :return: 302
    """
    data = {
        "name": "Advert_update",
        "budget": 122,
        "promotion_path": "news_news",
        "products": product.pk,
    }
    url = reverse("ads:ads-update", kwargs={"pk":ads.pk})
    response = client.post(url, data)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_update_by_user(auth_user, user, product, ads):
    """
    Тест проверки возможности обновления рекламной компании авторизованным пользователем.
    Возвращает код 302, обновляет рекламную компанию и направляет на страницу деталей рекламы
    при наличии определенных разрешений.
    :param client:  fixture
    :param ads:  fixture
    :param product:  fixture
    :return: 302
    """
    data = {
        "name": "Advert_update",
        "budget": 122,
        "promotion_path": "news_news",
        "products": product.pk,
    }
    url = reverse("ads:ads-update", kwargs={"pk": ads.pk})
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Advert)
    view_permission = Permission.objects.get(content_type=content_type, codename='view_advert')
    change_permission = Permission.objects.get(content_type=content_type, codename='change_advert')
    user.user_permissions.add(view_permission, change_permission)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    upd_ads = Advert.objects.get(name="Advert_update")
    assert upd_ads.budget == 122
    assert upd_ads.promotion_path == "news_news"


@pytest.mark.django_db
def test_update_by_admin(auth_admin, product, ads):
    """
    Тест проверки возможности обновления рекламной компании администратором.
    Возвращает код 302, обновляет рекламную компанию и направляет на страницу деталей рекламы.
    :param client:  fixture
    :param ads:  fixture
    :param product:  fixture
    :return: 302
    """
    data = {
        "name": "Advert_update",
        "budget": 122,
        "promotion_path": "news_news",
        "products": product.pk,
    }
    url = reverse("ads:ads-update", kwargs={"pk": ads.pk})
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    upd_ads = Advert.objects.get(name="Advert_update")
    assert upd_ads.budget == 122
    assert upd_ads.promotion_path == "news_news"
    assert "ads/1" in response.url


@pytest.mark.django_db
def test_delete_ads(client, user, product, ads):
    """
    Тест проверки невозможности удаления рекламной компании неавторизованным пользователем.
    Возвращает код 403.
    :param client:  fixture
    :param ads:  fixture
    :param product:  fixture
    :return: 403
    """
    url = reverse("ads:ads_delete", kwargs={"pk":ads.pk})
    response = client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_user(auth_user, user, product, ads):
    """
    Тест проверки возможности удаления рекламной компании авторизованным пользователем.
    Возвращает код 403.
    :param client:  fixture
    :param ads:  fixture
    :param product:  fixture
    :return: 403
    """
    url = reverse("ads:ads_delete", kwargs={"pk":ads.pk})
    response = auth_user.post(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Advert)
    view_permission = Permission.objects.get(content_type=content_type, codename='view_advert')
    delete_permission = Permission.objects.get(content_type=content_type, codename='delete_advert')
    user.user_permissions.add(view_permission, delete_permission)

    response = auth_user.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_admin(auth_admin, product, ads):
    """
    Тест проверки возможности удаления рекламной компании администратором.
    Возвращает код 302, удаляет рекламную компанию и направляет на страницу списка рекламы.
    :param client:  fixture
    :param ads:  fixture
    :param product:  fixture
    :return: 302
    """
    url = reverse("ads:ads_delete", kwargs={"pk":ads.pk})
    response = auth_admin.post(url)
    assert response.status_code == 302
    assert not  Advert.objects.filter(name="TestAdvert").exists()
