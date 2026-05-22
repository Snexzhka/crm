import datetime

import pytest
from django.contrib.auth.models import User
from django.test import Client
from pytest_django.fixtures import client

from products.models import Product
from leads.models import Lead
from ads.models import Advert
from tasks.models import Task
from contracts.models import Contract
from customers.models import Customer


@pytest.fixture
def user(db):
    return User.objects.create_user(
        username="TestUser",
             password="Test1999"
             )


@pytest.fixture
def product(db):
    return Product.objects.create(
        name="TestProd",
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
def task(db, user):
    return Task.objects.create(
        user=user,
        title = "TestTask",
        description="Desc",
        due_date=datetime.datetime.now(),
        is_completed=False,
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
def contract(db, product, lead):
    return Contract.objects.create(
        name="TestContract",
        cost=10000,
        products=product,
        lead=lead,
        duration=datetime.timedelta(days=5),
    )

@pytest.fixture
def customer(db, lead, contract):
    return Customer.objects.create(
        lead=lead,
        contract=contract,
    )

@pytest.fixture
def user_admin(db):
    return User.objects.create_superuser(
        username="Admin",
        password="Passwort111"
    )

@pytest.fixture
def auth_user(client, user):
    client.login(username=user.username,  password="Test1999")
    return client


@pytest.fixture
def auth_admin(client, user_admin):
    client.login(username=user_admin.username,  password="Passwort111")
    return client