import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import Advert
from products.models import Product

@pytest.mark.django_db
def test_product_create(ads):
    assert ads.name == "TestAdvert"
    assert ads.budget == 150


@pytest.mark.django_db
def test_view_ads(user, auth_user, ads):
    url = reverse("ads:ads-list")
    response = auth_user.get(url)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Advert)
    view_permission = Permission.objects.get(content_type=content_type, codename='view_advert')
    user.user_permissions.add(view_permission)

    response = auth_user.get(url)
    assert response.status_code == 200
    assert "ads" in response.context
    assert ads.budget == 150


@pytest.mark.django_db
def test_view_admin(auth_admin):
    url = reverse("ads:ads-list")
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert "user" in response.context
    assert len(response.context) == 2


@pytest.mark.django_db
def test_view(client, user):
    url = reverse("ads:ads-list")
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url

@pytest.mark.django_db
def test_view_detail(client, user, ads):
    url = reverse("ads:ads-detail", kwargs={"pk":ads.pk})
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_detail_user(auth_user, ads, user):
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
    url = reverse("ads:ads-detail", kwargs={"pk": ads.pk})
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert Advert.objects.count() == 1
    assert ads.budget == 150


@pytest.mark.django_db
def test_create_ads(client, ads, product):
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
def test_create_user(ads, auth_user, product, user):
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
def test_create_by_admin(auth_admin, admin_user, product, ads):
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
def test_update_by_admin(admin_user, auth_admin, product, ads):
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
    url = reverse("ads:ads_delete", kwargs={"pk":ads.pk})
    response = client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_delete_by_user(auth_user, user, product, ads):
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
def test_delete_admin(admin_user, auth_admin, product, ads):
    url = reverse("ads:ads_delete", kwargs={"pk":ads.pk})
    response = auth_admin.post(url)
    assert response.status_code == 302
    assert not  Advert.objects.filter(name="TestAdvert").exists()



