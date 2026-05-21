import pytest
from django.urls import reverse

from .models import Advert

@pytest.mark.django_db
def test_product_create(ads):
    assert ads.name == "TestAdvert"
    assert ads.budget == 150


@pytest.mark.django_db
def test_view_ads(auth_user):
    url = reverse("ads:ads-list")
    response = auth_user.get(url)
    assert response.status_code == 403
