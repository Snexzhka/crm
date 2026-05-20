import pygments
import pytest
from django.contrib.auth.models import User
from pytest_django.fixtures import client

from products.models import Product
from leads.models import Lead
from ads.models import Advert


@pytest.fixture
def user(db):
    return User.objects.create_user(username="TestUser", password="Test1999")


@pytest.fixture
def product(db):
    return Product.objects.create(
        name = "TestProd",
        description="TestDesc",
        cost=100,
    )

@pytest.fixture
def ads(db, product):
    return Advert.objects.create(
        name = "TestAdvert",
        products=product,
        promotion_path="testpromo",
        budget=150,
    )

@pytest.fixture
def lead(db, ads):
    return Lead.objects.create(
        first_name="Test",
        last_name="testych",
        phone="+234578",
        email="test@test.by",
        advert_name=ads,
    )
@pytest.fixture
def user_admin(db):
    return User.objects.create_superuser(name="Admin", password="Passwort111")

@pytest.fixture
def auth_user(db, user, user_admin):
    client.login(user.username,  password="pass")
    return client()