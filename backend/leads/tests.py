import os
import shutil

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client
from django.urls import reverse

from ads.models import Advert
from products.models import Product
from .models import Lead

class LeadsModelsTest(TestCase):
    """
    Класс проверки создания объекта моделей лидов
    """
    @classmethod
    def setUpClass(cls):
        """
        Метод установки данных для тестов, срабатывает вначале, перед прогоном всех тестов
        """
        super().setUpClass()
        cls.product = Product.objects.create(
            name="TestProd",
            description="Test",
            cost=100,
        )
        cls.advert = Advert.objects.create(
            name="TestAdvert",
            products=cls.product,
            promotion_path="news",
            budget=150,
        )

    def setUp(self):
        """
        Метод установки данных для тестов перед каждым тестов заново.
        """
        self.lead = Lead.objects.create(
            first_name="TestLead",
            last_name="TestLastLead",
            phone="+3456789",
            email="Lead@lead.ru",
            advert_name=self.advert,
        )

    def test_model_create(self):
        """
        Тест проверки правильности создания объектов модели лидов.
        """
        self.assertEqual(self.lead.first_name, "TestLead")
        self.assertEqual(self.advert.name, "TestAdvert")
        self.assertEqual(self.lead.email, "Lead@lead.ru")
        self.assertEqual(Lead.objects.count(), 1)


class LeadsViewTest(TestCase):
    """
    Класс проверки правильности работы представлений для лидов.
    """
    @classmethod
    def setUpClass(cls):
        """
        Метод, устанавливающий данные для тестов перед прогоном всех тестов.
        """
        super().setUpClass()
        cls.product = Product.objects.create(
            name="TestProd",
            description="Test",
            cost=100,
        )
        cls.advert = Advert.objects.create(
            name="TestAdvert",
            products=cls.product,
            promotion_path="news",
            budget=150,
        )
        cls.client = Client()
        cls.operator = User.objects.create_user(username="Operator", password="OperatorPassword")
        cls.admin = User.objects.create_superuser(username="Admin", password="AdminPassword")


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
        Метод установки значений перед каждым тестом.
        """
        self.lead = Lead.objects.create(
            first_name="TestLead",
            last_name="TestLastLead",
            phone="+3456789",
            email="Lead@lead.ru",
            advert_name=self.advert,
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


    def test_View_leads(self):
        """
        Тест проверки невозможности просмотра списка лидов неавторизованным пользователем.
        Возвращает код 302 и перенаправляет на страницу входа.
        """
        self.client.logout()
        response = self.client.get(reverse("leads:leads-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_leads_operator(self):
        """
        Тест проверки возможности просмотра списка лидов оператором. Возвращает изначально
        код 403, после предоставления разрешений - 200.
        """
        self.login_operator()
        response = self.client.get(reverse("leads:leads-list"))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Lead)
        permission = Permission.objects.get(content_type=content_type, codename='view_lead')
        self.operator.user_permissions.add(permission)

        response = self.client.get(reverse("leads:leads-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TestLead")


    def test_leads_admin(self):
        """
        Тест проверки возможности просмотра списка лидов оператором. Возвращает код 200.
        """
        self.login_admin()
        response = self.client.get(reverse("leads:leads-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "TestLastLead")


    def test_detail_leads(self):
        """
        Тест проверяющий невозможность просмотра деталей лида неавторизованным пользователем.
        Возвращает код 302 и перенаправляет на страницу входа.
        """
        self.client.logout()
        response = self.client.get(reverse("leads:leads-detail", kwargs={"pk":self.lead.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_operator_detail(self):
        """
        Тест, проверяющий возможность просмотра оператором деталей лидов. Изначально дает код 403,
        после предоставления разрешений 200.
        """
        self.login_operator()
        response = self.client.get(reverse("leads:leads-detail", kwargs={"pk": self.lead.pk}))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Lead)
        permission = Permission.objects.get(content_type=content_type, codename='view_lead')
        self.operator.user_permissions.add(permission)

        response = self.client.get(reverse("leads:leads-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.lead.first_name, "TestLead")

    def test_admin_detail(self):
        """
         Тест, проверяющий возможность просмотра админом деталей лидов. Возвращает код 200.
        """
        self.login_admin()
        response = self.client.get(reverse("leads:leads-detail", kwargs={"pk": self.lead.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Lead.objects.count(), 1)
        self.assertEqual(self.lead.advert_name.name, "TestAdvert")

    def test_create_lead(self):
        """
        Тест, проверяющий невозможность создания лида неавторизованным пользователем.
        Возвращает код 302 с перенаправлением на страницу входа.
        """
        self.client.logout()
        data = {
            "first_name":"TestL",
            "last_name":"TestLast",
            "phone":"+3456789",
            "email":"Lead@l.ru",
            "advert_name":self.advert.pk,
        }
        response = self.client.post(reverse("leads:leads-create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


    def test_operator_create(self):
        """
        Тест, проверяющий возможность создания лида оператором. Сразу возвращает код 403, после
        предоставления прав - 302 и перенаправляет на список лидов.
        """
        self.login_operator()
        ads_ct = ContentType.objects.get_for_model(Advert)
        prod_ct = ContentType.objects.get_for_model(Product)
        advert_permission = Permission.objects.get(content_type=ads_ct, codename='view_advert')
        product_permission = Permission.objects.get(content_type=prod_ct, codename='view_product')
        self.operator.user_permissions.add(advert_permission, product_permission)
        data = {
            "first_name": "TestL",
            "last_name": "TestLast",
            "phone": "+3456789",
            "email": "Lead@l.ru",
            "advert_name": self.advert.pk,
        }
        response = self.client.post(reverse("leads:leads-create"), data=data)
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Lead)
        view_permission = Permission.objects.get(content_type=content_type, codename='view_lead')
        add_permission = Permission.objects.get(content_type=content_type, codename='add_lead')
        self.operator.user_permissions.add(view_permission, add_permission)

        response = self.client.post(reverse("leads:leads-create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("leads:leads-list"))
        new_lead = Lead.objects.get(first_name="TestL")
        self.assertTrue(Lead.objects.filter(first_name="TestL").exists())
        self.assertEqual(new_lead.email, "Lead@l.ru")


    def test_admin_create(self):
        """
        Тест, проверяющий возможность создания лида админом. Возвращает код 302 и
        перенаправляет на список лидов.
        """
        self.login_admin()
        data = {
            "first_name": "TestL",
            "last_name": "TestLast",
            "phone": "+3456789",
            "email": "Lead@l.ru",
            "advert_name": self.advert.pk,
        }
        response = self.client.post(reverse("leads:leads-create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("leads:leads-list"))
        new_lead = Lead.objects.get(first_name="TestL")
        self.assertTrue(Lead.objects.filter(first_name="TestL").exists())
        self.assertEqual(new_lead.advert_name.promotion_path, "news")

    def  test_update_leads(self):
        """
        Тест, проверяющий невозможность обновления лида неавторизованным пользователем.
        Возвращает код 302 с перенаправлением на страницу входа.
        """
        self.client.logout()
        data = {
            "first_name": "Lead1Test",
            "last_name": "LastName",
            "phone": "+3456789",
            "email": "Lead@my.ru",
            "advert_name": self.advert.pk,
        }
        response = self.client.post(reverse("leads:leads-update", kwargs={"pk":self.lead.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_operator_update(self):
        """
         Тест, проверяющий возможность обновления лида оператором. Сразу возвращает код 403, после
        предоставления прав - 302 и перенаправляет на список лидов.
        """
        self.login_operator()
        ads_ct = ContentType.objects.get_for_model(Advert)
        prod_ct = ContentType.objects.get_for_model(Product)
        advert_permission = Permission.objects.get(content_type=ads_ct, codename='view_advert')
        product_permission = Permission.objects.get(content_type=prod_ct, codename='view_product')
        self.operator.user_permissions.add(advert_permission, product_permission)
        data = {
            "first_name": "Lead1Test",
            "last_name": "LastName",
            "phone": "+3456789",
            "email": "Lead@my.ru",
            "advert_name": self.advert.pk,
        }
        response = self.client.post(reverse("leads:leads-update", kwargs={"pk": self.lead.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Lead)
        view_permission = Permission.objects.get(content_type=content_type, codename='view_lead')
        change_permission = Permission.objects.get(content_type=content_type, codename='change_lead')
        self.operator.user_permissions.add(view_permission, change_permission)

        response = self.client.post(reverse("leads:leads-update", kwargs={"pk": self.lead.pk}),
                                    data=data)
        self.product.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("leads:leads-detail", kwargs={"pk": self.lead.pk}))
        update_lead = Lead.objects.get(last_name="LastName")
        self.assertEqual(update_lead.first_name, "Lead1Test")
        self.assertTrue(Lead.objects.filter(last_name="LastName").exists())


    def test_admin_update(self):
        """
        Тест, проверяющий возможность обновления лида админом. Возвращает код 302 и
        перенаправляет на список лидов.
        """
        self.login_admin()
        data = {
            "first_name": "Lead1Test",
            "last_name": "LastName",
            "phone": "+3456789",
            "email": "Lead@my.ru",
            "advert_name": self.advert.pk,
        }
        response = self.client.post(reverse("leads:leads-update", kwargs={"pk": self.lead.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("leads:leads-detail", kwargs={"pk": self.lead.pk}))
        update_lead = Lead.objects.get(last_name="LastName")
        self.assertTrue(Lead.objects.filter(last_name="LastName").exists())
        self.assertEqual(update_lead.first_name, "Lead1Test")


    def test_delete_leads(self):
        """
        Тест, проверяющий невозможность удаления лида неавторизованным пользователем.
        Возвращает код 403.
        """
        self.client.logout()
        response  = self.client.post(reverse("leads:leads-delete", kwargs={"pk": self.lead.pk}))
        self.assertEqual(response.status_code, 403)


    def tset_operator_delete(self):
        """
        Тест, проверяющий возможность удаления лида оператором. Сразу возвращает код 403, после
        предоставления прав - 403 (согласно представления удалить может только админ).
        """
        self.login_operator()
        ads_ct = ContentType.objects.get_for_model(Advert)
        prod_ct = ContentType.objects.get_for_model(Product)
        advert_permission = Permission.objects.get(content_type=ads_ct, codename='view_advert')
        product_permission = Permission.objects.get(content_type=prod_ct, codename='view_product')
        self.operator.user_permissions.add(advert_permission, product_permission)

        response = self.client.post(reverse("leads:leads-delete", kwargs={"pk": self.lead.pk}))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Lead)
        view_permission = Permission.objects.get(content_type=content_type, codename='view_lead')
        delete_permission = Permission.objects.get(content_type=content_type, codename='delete_lead')
        self.operator.user_permissions.add(view_permission, delete_permission)

        response = self.client.post(reverse("leads:leads-delete", kwargs={"pk": self.lead.pk}))
        self.assertEqual(response.status_code, 403)


    def test_admin_delete(self):
        """
        Тест, проверяющий возможность удаления лида админом. Возвращает код 302 и
        перенаправляет на список лидов.
        """
        self.login_admin()
        response = self.client.post(reverse("leads:leads-delete", kwargs={"pk": self.lead.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("leads:leads-list"))
        self.assertFalse(Lead.objects.filter(first_name="TestLead").exists())