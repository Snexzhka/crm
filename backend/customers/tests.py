"""
Тесты на основе TestCase
"""

import os
import shutil
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client
from django.urls import reverse

from ads.models import Advert
from contracts.models import Contract
from leads.models import Lead
from products.models import Product
from .models import Customer

User = get_user_model()


class CustomerModelGTest(TestCase):
    """
    Класс проверки создания объектов модели активных клиентов
    """

    @classmethod
    def setUpClass(cls):
        """
        Метод установки значений для тестов, который срабатывает вначале, перед
        прогоном всех тестов.
        """

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
        """
        Метод установки данных для тестов перед каждым тестов заново.
        """

        self.customer = Customer.objects.create(
            lead=self.lead,
            contract=self.contract,
        )

    def test_customer_model(self):
        """
        Тест проверки создания моделей активных клиентов
        """

        self.assertEqual(self.customer.lead.first_name, "TestLead")
        self.assertEqual(self.customer.contract.name, "TestContract")


class CustomerViewTest(TestCase):
    """
    Класс проверки работы представлений.
    """

    @classmethod
    def setUpClass(cls):
        """
        Метод установки значений для тестов, который срабатывает вначале, перед
        прогоном всех тестов.
        """

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
        cls.operator = User.objects.create_user(
            username="Operator", password="OperatorPassword"
        )
        cls.admin = User.objects.create_superuser(
            username="Admin", password="AdminPassword"
        )

    def setUp(self):
        """
        Метод установки данных для тестов перед каждым тестов заново.
        """

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
        Метод для удаления медиа файлов после прогона всех тестов. Запускается в конце, после
        отработки всех тестов.
        """

        # Проверяем, существует ли переопределённая настройка
        if hasattr(cls, "_overridden_settings") and cls._overridden_settings:
            media_root = cls._overridden_settings.get("MEDIA_ROOT")
            if media_root and os.path.exists(media_root):
                shutil.rmtree(media_root, ignore_errors=True)
        super().tearDownClass()

    def test_customer_view(self):
        """
        Тест проверки невозможности просмотра списка активных клиентов
        неавторизованным пользователем. Возвращает код 302 и перенаправляет на
        страницу входа.
        """

        self.client.logout()
        response = self.client.get(reverse("customers:customers-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_operator_view(self):
        """
        Тест проверки возможности просмотра списка активных клиентов
        авторизованным пользователем. Возвращает код 403, после наделения
        необходимыми правами - 200.
        """

        self.login_operator()
        response = self.client.get(reverse("customers:customers-list"))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Customer)
        permission = Permission.objects.get(
            content_type=content_type, codename="view_customer"
        )
        self.operator.user_permissions.add(permission)

        response = self.client.get(reverse("customers:customers-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.customer.lead.first_name, "TestLead")

    def test_admin_view(self):
        """
        Тест проверки возможности просмотра списка активных клиентов
        администратором. Возвращает код 200.
        """

        self.login_admin()
        response = self.client.get(reverse("customers:customers-list"))
        self.assertEqual(response.status_code, 200)

    def test_detail_view(self):
        """
        Тест проверки невозможности просмотра деталей активного клиента
        неавторизованным пользователем. Возвращает код 302 и перенаправляет на
        страницу входа.
        """

        self.client.logout()
        response = self.client.get(
            reverse("customers:customers-detail", kwargs={"pk": self.customer.pk}),
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_operator_detail(self):
        """
        Тест проверки возможности просмотра деталей активного клиента
        авторизованным пользователем. Возвращает код 403, после наделения необходимыми
        правами - 200.
        """

        self.login_operator()
        response = self.client.get(
            reverse("customers:customers-detail", kwargs={"pk": self.customer.pk}),
        )
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Customer)
        permission = Permission.objects.get(
            content_type=content_type, codename="view_customer"
        )
        self.operator.user_permissions.add(permission)

        response = self.client.get(
            reverse("customers:customers-detail", kwargs={"pk": self.customer.pk}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.customer.contract.name, "TestContract")

    def test_admin_detail(self):
        """
        Тест проверки возможности просмотра деталей активного клиента
        администратором. Возвращает код 200.
        """

        self.login_admin()
        response = self.client.get(
            reverse("customers:customers-detail", kwargs={"pk": self.customer.pk}),
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.customer.contract.name, "TestContract")

    def test_customer_create(self):
        """
        Тест проверки невозможности создания активного клиента неавторизованным
        пользователем. Возвращает код 302 и перенаправляет на
        страницу входа.
        """

        self.client.logout()
        self.leads = Lead.objects.create(
            first_name="TestL",
            last_name="TestLastLead",
            phone="+3456789",
            email="Lead@lead.ru",
            advert_name=self.advert,
        )

        self.contracts = Contract.objects.create(
            name="TestCont",
            products=self.product,
            duration=timedelta(days=5),
            cost=120,
            lead=self.lead,
        )

        data = {
            "lead": self.lead.pk,
            "contract": self.contract.pk,
        }
        response = self.client.post(reverse("customers:customers-create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_operator_create(self):
        """
        Тест проверки возможности создания активного клиента авторизованным
        пользователем. Возвращает код 403, после получения всех прав - 302 и перенаправляет на
        страницу списка клиентов.
        """

        self.login_operator()
        initial_count = Customer.objects.count()

        product_ct = ContentType.objects.get_for_model(Product)
        prod_permission = Permission.objects.get(
            content_type=product_ct, codename="add_product"
        )
        advert_ct = ContentType.objects.get_for_model(Advert)
        ads_permission = Permission.objects.get(
            content_type=advert_ct, codename="add_advert"
        )
        contract_ct = ContentType.objects.get_for_model(Contract)
        cont_permission = Permission.objects.get(
            content_type=contract_ct, codename="add_contract"
        )
        lead_ct = ContentType.objects.get_for_model(Lead)
        lead_permission = Permission.objects.get(
            content_type=lead_ct, codename="add_lead"
        )
        self.operator.user_permissions.add(
            prod_permission, ads_permission, cont_permission, lead_permission
        )

        data = {
            "lead": self.lead.pk,
            "contract": self.contract.pk,
        }

        response = self.client.post(
            reverse("customers:customers-create"),
            data=data,
        )
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Customer)
        add_permission = Permission.objects.get(
            content_type=content_type, codename="add_customer"
        )
        view_permission = Permission.objects.get(
            content_type=content_type, codename="view_customer"
        )
        self.operator.user_permissions.add(view_permission, add_permission)

        response = self.client.post(
            reverse("customers:customers-create"),
            data=data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("customers:customers-list"))
        self.assertEqual(Customer.objects.count(), initial_count + 1)
        new_cust = Customer.objects.last()
        self.assertEqual(new_cust.lead, self.lead)
        self.assertEqual(new_cust.contract, self.contract)

    def test_admin_create(self):
        """
        Тест проверки возможности создания активного клиента администратором.
        Возвращает код - 302 и перенаправляет на страницу списка клиентов.
        """

        self.login_admin()
        initial_count = Customer.objects.count()
        data = {
            "lead": self.lead.pk,
            "contract": self.contract.pk,
        }

        response = self.client.post(
            reverse("customers:customers-create"),
            data=data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("customers:customers-list"))
        self.assertEqual(Customer.objects.count(), initial_count + 1)
        new_cust = Customer.objects.last()
        self.assertEqual(new_cust.lead, self.lead)
        self.assertEqual(new_cust.contract, self.contract)

    def test_update_customer(self):
        """
        Тест проверки невозможности обновления активного клиента неавторизованным
        пользователем. Возвращает код 302 и перенаправляет на
        страницу входа.
        """

        self.client.logout()
        data = {
            "lead": self.lead.pk,
            "contract": self.contract.pk,
        }
        response = self.client.post(
            reverse("customers:customer_update", kwargs={"pk": self.customer.pk}),
            data=data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_operator_update(self):
        """
        Тест проверки возможности обновления активного клиента авторизованным
        пользователем. Возвращает код 403, после получения всех прав - 302 и перенаправляет на
        страницу деталей клиентов.
        """
        self.login_operator()

        product_ct = ContentType.objects.get_for_model(Product)
        prod_permission = Permission.objects.get(
            content_type=product_ct, codename="add_product"
        )
        advert_ct = ContentType.objects.get_for_model(Advert)
        ads_permission = Permission.objects.get(
            content_type=advert_ct, codename="add_advert"
        )
        contract_ct = ContentType.objects.get_for_model(Contract)
        cont_permission = Permission.objects.get(
            content_type=contract_ct, codename="add_contract"
        )
        lead_ct = ContentType.objects.get_for_model(Lead)
        lead_permission = Permission.objects.get(
            content_type=lead_ct, codename="add_lead"
        )
        self.operator.user_permissions.add(
            prod_permission, ads_permission, cont_permission, lead_permission
        )

        data = {
            "lead": self.lead.pk,
            "contract": self.contract.pk,
        }
        response = self.client.post(
            reverse("customers:customer_update", kwargs={"pk": self.customer.pk}),
            data=data,
        )
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Customer)
        change_permission = Permission.objects.get(
            content_type=content_type, codename="change_customer"
        )
        view_permission = Permission.objects.get(
            content_type=content_type, codename="view_customer"
        )
        self.operator.user_permissions.add(view_permission, change_permission)

        response = self.client.post(
            reverse("customers:customer_update", kwargs={"pk": self.customer.pk}),
            data=data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("customers:customers-detail", kwargs={"pk": self.customer.pk}),
        )

        upd_cust = Customer.objects.last()
        self.assertEqual(upd_cust.lead, self.lead)
        self.assertEqual(upd_cust.contract, self.contract)

    def test_admin_update(self):
        """
        Тест проверки возможности обновления активного клиента администратором.
        Возвращает код - 302 и перенаправляет на страницу деталей клиентов.
        """

        self.login_admin()
        data = {
            "lead": self.lead.pk,
            "contract": self.contract.pk,
        }
        response = self.client.post(
            reverse("customers:customer_update", kwargs={"pk": self.customer.pk}),
            data=data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            reverse("customers:customers-detail", kwargs={"pk": self.customer.pk}),
        )

        upd_cust = Customer.objects.last()
        self.assertEqual(upd_cust.lead, self.lead)
        self.assertEqual(upd_cust.contract, self.contract)

    def test_delete_customer(self):
        """
        Тест проверки невозможности удаления активного клиента неавторизованным
        пользователем. Возвращает код 302 и перенаправляет на
        страницу входа.
        """

        self.client.logout()
        response = self.client.post(
            reverse("customers:customer-delete", kwargs={"pk": self.customer.pk}),
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_operator_delete(self):
        """
        Тест проверки возможности удаления активного клиента авторизованным
        пользователем. Возвращает код 403, и после получения всех прав - 403 так как
        удаление разрешено только администратору.
        """

        self.login_operator()
        response = self.client.post(
            reverse("customers:customer-delete", kwargs={"pk": self.customer.pk}),
        )
        self.assertEqual(response.status_code, 403)

        product_ct = ContentType.objects.get_for_model(Product)
        prod_permission = Permission.objects.get(
            content_type=product_ct, codename="add_product"
        )
        advert_ct = ContentType.objects.get_for_model(Advert)
        ads_permission = Permission.objects.get(
            content_type=advert_ct, codename="add_advert"
        )
        contract_ct = ContentType.objects.get_for_model(Contract)
        cont_permission = Permission.objects.get(
            content_type=contract_ct, codename="add_contract"
        )
        lead_ct = ContentType.objects.get_for_model(Lead)
        lead_permission = Permission.objects.get(
            content_type=lead_ct, codename="add_lead"
        )
        self.operator.user_permissions.add(
            prod_permission, ads_permission, cont_permission, lead_permission
        )

        content_type = ContentType.objects.get_for_model(Customer)
        delete_permission = Permission.objects.get(
            content_type=content_type,
            codename="delete_customer",
        )
        view_permission = Permission.objects.get(
            content_type=content_type,
            codename="view_customer",
        )
        self.operator.user_permissions.add(view_permission, delete_permission)

        response = self.client.post(
            reverse("customers:customer-delete", kwargs={"pk": self.customer.pk}),
        )
        self.assertEqual(response.status_code, 403)

    def test_admin_delete(self):
        """
        Тест проверки возможности удаления активного клиента администратором.
        Возвращает код - 302 и перенаправляет на страницу списка клиентов.
        """

        self.login_admin()
        response = self.client.post(
            reverse("customers:customer-delete", kwargs={"pk": self.customer.pk}),
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("customers:customers-list"))
