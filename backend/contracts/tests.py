import datetime
import os
import shutil
from datetime import timedelta
from io import BytesIO

from django.contrib.contenttypes.models import ContentType
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from .models import Contract
from ads.models import Advert
from leads.models import Lead
from products.models import Product


class ContractModelTest(TestCase):
    """
    Класс для тестирования создания объектов модели контракта
    """
    def setUp(self):
        """
        Метод установки значений для тестов перед проведением каждого теста заново
        """
        self.product = Product.objects.create(
            name="TestProduct",
            cost=100,
            description="qwerty",
        )
        self.ads = Advert.objects.create(
            name="TestAdvert",
            products=self.product,
            promotion_path="news",
            budget=77,
        )
        self.lead = Lead.objects.create(
            first_name="Test",
            last_name="Testovich",
            phone="+1234567",
            email="test@test.ru",
            advert_name=self.ads,
        )
        self.contract = Contract.objects.create(
            name="TestContract",
            products=self.product,
            duration=timedelta(days=5),
            cost=120,
            lead=self.lead,
        )


    def test_model_contract(self):
        """
        Тест проверки создания моделей контракта
        """
        self.assertEqual(self.contract.name, "TestContract")
        self.assertNotEqual(self.contract.cost, 1100)
        self.assertEqual(self.contract.products.name, "TestProduct")
        self.assertEqual(str(self.contract.start_date), str(datetime.datetime.now().date()))
        self.assertEqual(Contract.objects.count(), 1)
        self.assertEqual(self.contract.lead.phone, "+1234567")


class ContractTestView(TestCase):
    """
    Класс проверки представлений для контрактов
    """
    @classmethod
    def setUpClass(cls):
        """
        Метод, устанавливающий значения для всех тестов перед запуском первого теста. Значения используются
        на протяжении всего тестирования. Используется для данных, используемых в каждом тесте в целях
        экономии ресурсов.
        """
        super().setUpClass()
        cls.client = Client()

        cls.manager = User.objects.create_user(
            username="Manager",
            password="ManagerPassword")
        cls.admin = User.objects.create_superuser(
            username="Admin",
            password="AdminPassword")
        cls.product = Product.objects.create(
            name="TestProduct",
            cost=100,
            description="qwerty",
        )
        cls.ads = Advert.objects.create(
            name="TestAdvert",
            products=cls.product,
            promotion_path="news",
            budget=77,
        )
        cls.lead = Lead.objects.create(
            first_name="Test",
            last_name="Testovich",
            phone="+1234567",
            email="test@test.ru",
            advert_name=cls.ads,
        )

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

    def setUp(self):
        """
        Метод установки значений для тестов, используется перед каждым тестом заново.
        Используется для данных, изменяемых в каждом тесте.
        """
        self.contract = Contract.objects.create(
            name="TestContract",
            products=self.product,
            duration=timedelta(days=5),
            cost=120,
            lead=self.lead,
        )

    def login_manager(self):
        """
        Метод для входа менеджера, можно было обозвать юзером, но согласно ТЗ "Менеджер"
        """
        return self.client.login(
            username="Manager",
            password="ManagerPassword"
        )

    def login_admin(self):
        """
        Метод для входа администратора.
        """
        return self.client.login(
            username="Admin",
            password="AdminPassword"
        )

    def test_list_view_contract(self):
        """
        Тест проверки невозможности просмотра списка контрактов неавторизованным пользователем.
        Возвращает код 302 и перенаправляет на страницу входа.
        """
        self.client.logout()
        response = self.client.get(reverse("contracts:contracts-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_list_contract_manager(self):
        """
        Тест проверки возможности просмотра списка контрактов авторизованным пользователем.
        Возвращает код 403 - нет доступа. После предоставления необходимых разрешений -
        возвращает код 200.
        """
        self.login_manager()
        response = self.client.get(reverse("contracts:contracts-list"))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Contract)
        permission = Permission.objects.get(content_type=content_type, codename='view_contract')
        self.manager.user_permissions.add(permission)

        response = self.client.get(reverse("contracts:contracts-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.contract.name, "TestContract")
        self.assertNotEqual(self.contract.cost, 1000)

    def test_list_contract_admin(self):
        """
        Тест проверки возможности просмотра администратором списка контрактов без
        предоставления дополнительных прав, сразу возвращается код 200.
        """
        self.login_admin()
        response = self.client.get(reverse("contracts:contracts-list"))
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(self.contract.lead.first_name, "Tom")
        self.assertEqual(self.contract.cost, 120)


    def test_detail_view(self):
        """
        Тест проверки невозможности просмотра деталей контракта неавторизованным пользователем.
        Возвращает код 302 и перенаправляет на страницу входа.
        """
        self.client.logout()
        response = self.client.get(reverse("contracts:contracts-detail", kwargs={"pk":self.contract.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_detail_manager(self):
        """
        Тест проверки возможности просмотра деталей контракта авторизованным пользователем.
        Без разрешений возвращает код 403, после их предоставления - 200.
        """
        self.login_manager()
        response = self.client.get(reverse("contracts:contracts-detail", kwargs={"pk": self.contract.pk}))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Contract)
        permission = Permission.objects.get(content_type=content_type, codename='view_contract')
        self.manager.user_permissions.add(permission)

        response = self.client.get(reverse("contracts:contracts-detail", kwargs={"pk": self.contract.pk}))
        self.assertEqual(response.status_code, 200)

    def test_detail_admin(self):
        """
        Тест, подтверждающий возможность администратора просматривать детали контракта без
        предоставления дополнительных прав. Возвращает код 200.
        """
        self.login_admin()
        response = self.client.get(reverse("contracts:contracts-detail", kwargs={"pk": self.contract.pk}))
        self.assertEqual(response.status_code, 200)


    def test_create_contract(self):
        """
        Тест проверки невозможности создания контракта неавторизованным пользователем.
        Логичен возврат кода 302 и перенаправление на страницу входа.
        """
        self.client.logout()
        data = {
            "name":"TestCont",
            "products":self.product.pk,
            "duration": "7 days",
            "cost":'12',
            "lead":self.lead.pk,
        }
        response = self.client.post(reverse("contracts:contracts_create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_create_manager(self):
        """
        Тест проверки создания контракта авторизованным пользователем. Без наличия необходимых
        разрешений возвращается код 403, после их получения 302, создается контракт и идет
        перенаправлением на страницу списка контрактов.
        """
        self.login_manager()
        product_ct = ContentType.objects.get_for_model(Product)
        lead_ct = ContentType.objects.get_for_model(Lead)
        view_product = Permission.objects.get(content_type=product_ct, codename='view_product')
        view_lead = Permission.objects.get(content_type=lead_ct, codename='view_lead')
        self.manager.user_permissions.add(view_product, view_lead)
        data = {
            "name": "TestCont",
            "products": self.product.pk,
            "duration": "7 00:00:00",
            "cost": '12',
            "lead": self.lead.pk,
        }
        self.product.is_active = True
        self.product.save()
        response = self.client.post(reverse("contracts:contracts_create"), data=data)
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Contract)
        view_perm = Permission.objects.get(content_type=content_type, codename='view_contract')
        add_perm = Permission.objects.get(content_type=content_type, codename='add_contract')
        self.manager.user_permissions.add(view_perm, add_perm)

        response = self.client.post(reverse("contracts:contracts_create"), data=data)
        # if response.status_code == 200:
        #     print(response.context['form'].errors)
        #     self.fail("Форма не прошла валидацию")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("contracts:contracts-list"))
        self.assertTrue(Contract.objects.filter(name="TestCont").exists())
        new_contract = Contract.objects.get(name="TestCont")
        self.assertEqual(new_contract.cost, 12)


    def test_create_admin(self):
        """
        Тест проверки возможности создания нового контракта админом.
        Создается контракт и возвращается код 302 с перенаправлением наи страницу списка
        контрактов.
        """
        self.login_admin()
        data = {
            "name": "TestCont",
            "products": self.product.pk,
            "duration": "7 00:00:00",
            "cost": '12',
            "lead": self.lead.pk,
        }
        self.product.is_active = True
        self.product.save()
        response = self.client.post(reverse("contracts:contracts_create"), data=data)
        if response.status_code == 200:
            print(response.context['form'].errors)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("contracts:contracts-list"))
        self.assertTrue(Contract.objects.filter(name="TestCont").exists())
        new_contract = Contract.objects.get(name="TestCont")
        self.assertEqual(new_contract.name, "TestCont")
        self.assertNotEqual(new_contract.lead.pk, 4)


    def test_update_view(self):
        """
        Тест проверки невозможности обновления контракта неавторизованным пользователем.
        Возвращает код 302 и перенаправляет на страницу входа.
        """
        self.client.logout()
        data = {
            "name": "TestCont",
            "products": self.product.pk,
            "duration": "7 00:00:00",
            "cost": '12',
            "lead": self.lead.pk,
        }
        response = self.client.post(reverse("contracts:contract-update", kwargs={"pk":self.contract.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


    def test_update_manager(self):
        """
        Тест проверки возможности обновления контракта менеджером. Возвращает код 403, после
        предоставления необходимых разрешений - 302 с обновлением полей контракта и перенаправлением
        на страницу деталей контракта.
        """
        self.login_manager()
        product_ct = ContentType.objects.get_for_model(Product)
        lead_ct = ContentType.objects.get_for_model(Lead)
        view_product = Permission.objects.get(content_type=product_ct, codename='view_product')
        view_lead = Permission.objects.get(content_type=lead_ct, codename='view_lead')
        self.manager.user_permissions.add(view_product, view_lead)
        data = {
            "name": "TestCont",
            "products": self.product.pk,
            "duration": "7 00:00:00",
            "cost": '18',
            "lead": self.lead.pk,
        }
        response = self.client.post(reverse("contracts:contract-update", kwargs={"pk": self.contract.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Contract)
        view_perm = Permission.objects.get(content_type=content_type, codename='view_contract')
        change_perm = Permission.objects.get(content_type=content_type, codename='change_contract')
        self.manager.user_permissions.add(view_perm, change_perm)

        response = self.client.post(reverse("contracts:contract-update",kwargs={"pk": self.contract.pk}),
                                    data=data)
        self.product.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("contracts:contracts-detail", kwargs={"pk":self.contract.pk}))
        self.assertTrue(Contract.objects.filter(name="TestCont").exists())
        new_contract = Contract.objects.get(name="TestCont")
        self.assertEqual(new_contract.cost, 18)


    def test_update_admin(self):
        """
        Тест проверки возможности обновления полей контракта админом. Возвращает
        код 302 с перенаправлением на страницу деталей контракта.
        """
        self.login_admin()
        data = {
            "name": "TestCont",
            "products": self.product.pk,
            "duration": "7 00:00:00",
            "cost": '12',
            "lead": self.lead.pk,
        }
        response = self.client.post(reverse("contracts:contract-update", kwargs={"pk": self.contract.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("contracts:contracts-detail", kwargs={"pk": self.contract.pk}))
        self.assertTrue(Contract.objects.filter(name="TestCont").exists())
        new_contract = Contract.objects.get(name="TestCont")
        self.assertEqual(new_contract.products.name, "TestProduct")

    def test_delete_contract(self):
        """
        Тест проверки невозможности удаления контракта неавторизованным пользователем.
        Возвращает код 302 с перенаправлением на страницу входа.
        """
        self.client.logout()
        response = self.client.post(reverse("contracts:contract-delete", kwargs={"pk":self.contract.pk}))
        self.assertEqual(response.status_code, 403)


    def test_delete_manager(self):
        """
        Тест проверки невозможности удаления контракта менеджером. Даже после получения
        специальных разрешений возвращается код 403, так как такое поведение зашито в представлении -
        удалять разрешено только админу.
        """
        self.login_manager()
        response = self.client.post(reverse("contracts:contract-delete", kwargs={"pk": self.contract.pk}))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Contract)
        view_perm = Permission.objects.get(content_type=content_type, codename='view_contract')
        delete_perm = Permission.objects.get(content_type=content_type, codename='delete_contract')
        self.manager.user_permissions.add(view_perm, delete_perm)

        response = self.client.post(reverse("contracts:contract-delete", kwargs={"pk": self.contract.pk}))
        self.assertEqual(response.status_code, 403)


    def test_delete_admin(self):
        """
        Тест проверки удаления контракта админом. Происходит удаление, возвращается код 302 и
        перенаправление на страницу списка контрактов.
        """
        self.login_admin()
        response = self.client.post(reverse("contracts:contract-delete", kwargs={"pk": self.contract.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("contracts:contracts-list"))
