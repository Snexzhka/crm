import os
import shutil
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase, Client

from .models import Customer
from products.models import Product
from contracts.models import Contract
from leads.models import Lead
from ads.models import Advert


class CustomerModelGTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.product = Product.objects.create(
            name="TestProduct",
            cost=100,
            description="qwerty",
        )

        cls.advert = Advert.objects.create(
            name="TestAdvert",
            products=cls.product,
            promotion_path="news",
            budget=150,
        )

        cls.lead = Lead.objects.create(
            first_name="TestLead",
            last_name="TestLastLead",
            phone="+3456789",
            email="Lead@lead.ru",
            advert_name=cls.advert,
        )

        cls.contract = Contract.objects.create(
            name="TestContract",
            products=cls.product,
            duration=timedelta(days=5),
            cost=120,
            lead=cls.lead,
        )

    def setUp(self):
        self.customer = Customer.objects.create(
            lead=self.lead,
            contract=self.contract,
        )

    def test_customer_model(self):
        self.assertEqual(self.customer.lead.first_name, "TestLead")
        self.assertEqual(self.customer.contract.name, "TestContract")


class CustomerViewTest(TestCase):
    def setUpClass(cls):
        super().setUpClass()
        cls.product = Product.objects.create(
            name="TestProduct",
            cost=100,
            description="qwerty",
        )

        cls.advert = Advert.objects.create(
            name="TestAdvert",
            products=cls.product,
            promotion_path="news",
            budget=150,
        )

        cls.lead = Lead.objects.create(
            first_name="TestLead",
            last_name="TestLastLead",
            phone="+3456789",
            email="Lead@lead.ru",
            advert_name=cls.advert,
        )

        cls.contract = Contract.objects.create(
            name="TestContract",
            products=cls.product,
            duration=timedelta(days=5),
            cost=120,
            lead=cls.lead,
        )

        cls.client = Client()
        cls.operator = User.objects.create_user(username="Operator", password="OperatorPassword")
        cls.admin = User.objects.create_superuser(username="Admin", password="AdminPassword")

    def setUp(self):
        self.customer = Customer.objects.create(
            lead=self.lead,
            contract=self.contract,
        )

    def login_operator(self):
        """
        Метод, используемый для входа под именем оператора (согласно ТЗ)

        """
        return self.client.login(username="Operator", password="OperatorPassword")

    def login_admin(self):
        """
         Метод, используемый для входа под именем админа.

        """
        return self.client.login(username="Admin", password="AdminPassword")

    @classmethod
    def tearDownClass(cls):
        """
        Класс для удаления медиа файлов после прогона всех тестов. Запускается в конце, после
        отработки всех тестов.
        """
        # Проверяем, существует ли переопределённая настройка
        if hasattr(cls, '_overridden_settings') and cls._overridden_settings:
            media_root = cls._overridden_settings.get('MEDIA_ROOT')
            if media_root and os.path.exists(media_root):
                shutil.rmtree(media_root, ignore_errors=True)
        super().tearDownClass()

