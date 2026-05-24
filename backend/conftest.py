import datetime

import pytest
from django.contrib.auth import get_user_model

from ads.models import Advert
from contracts.models import Contract
from customers.models import Customer
from leads.models import Lead
from products.models import Product
from tasks.models import Task

# from pytest_django.fixtures import client

User = get_user_model()

# pylint: disable=redefined-outer-name


@pytest.fixture
def user(db):
    """
    Фикстура создания пользователя.
    :param db: SQLite
    :return: user
    """
    return User.objects.create_user(username="TestUser", password="Test1999")


@pytest.fixture
def product(db):
    """
    Фикстура создания услуги
    :param db: SQLite
    :return: product
    """
    return Product.objects.create(
        name="TestProd",
        description="TestDesc",
        cost=100,
    )


@pytest.fixture
def ads(db, product):
    """
    Фикстура создания рекламной компании
    :param db: SQLite
    :param product: product
    :return: advert
    """
    return Advert.objects.create(
        name="TestAdvert",
        products=product,
        promotion_path="testpromo",
        budget=150,
    )


@pytest.fixture
def task(db, user):
    """
    Фикстура создания текущей задачи
    :param db: SQLite
    :param user: user
    :return: task
    """
    return Task.objects.create(
        user=user,
        title="TestTask",
        description="Desc",
        due_date=datetime.datetime.now(),
        is_completed=False,
    )


@pytest.fixture
def lead(db, ads):
    """
    Фикстура создания потенциального клиента
    :param db: SQLite
    :param ads: advert
    :return: lead
    """
    return Lead.objects.create(
        first_name="Test",
        last_name="testych",
        phone="+234578",
        email="test@test.by",
        advert_name=ads,
    )


@pytest.fixture
def contract(db, product, lead):
    """
    Фикстура создания контракта
    :param db: SQLite
    :param product: product
    :param lead: lead
    :return: contract
    """
    return Contract.objects.create(
        name="TestContract",
        cost=10000,
        products=product,
        lead=lead,
        duration=datetime.timedelta(days=5),
    )


@pytest.fixture
def customer(db, lead, contract):
    """
    Фикстура создания активного пользователя
    :param db: SQLite
    :param lead: lead
    :param contract: contract
    :return: customer
    """
    return Customer.objects.create(
        lead=lead,
        contract=contract,
    )


@pytest.fixture
def user_admin(db):
    """
    Фикстура создания администратора
    :param db: SQLite
    :return: user_admin
    """
    return User.objects.create_superuser(username="Admin", password="Passwort111")


@pytest.fixture
def auth_user(client, user):
    """
    Фикстура входа от имени пользователя
    :param client: client
    :param user: user
    :return: client
    """
    client.login(username=user.username, password="Test1999")
    return client


@pytest.fixture
def auth_admin(client, user_admin):
    """
    Фикстура входа от имени администратора
    :param client: client
    :param user_admin: user_admin
    :return: client
    """
    client.login(username=user_admin.username, password="Passwort111")
    return client
