import os
import shutil

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from django.utils import timezone

from .models import Product


class ProductModelTest(TestCase):
    """
    Класс проверки создания объектов услуг.
    """
    def setUp(self):
        """
        Метод, устанавливающий значения перед каждым тестом заново.
        """
        self.product = Product.objects.create(
            name="testProduct",
            cost=12.21,
        )


    def test_add_product(self):
        """
        Тест, проверки создания объектов услуг
        """
        self.assertEqual(self.product.pk, 1)
        self.assertEqual(self.product.name, "testProduct")
        self.assertEqual(self.product.description, "")
        self.assertEqual(self.product.cost, 12.21)
        self.assertNotEqual(self.product.name, "Product")


class ProductTestView(TestCase):
    """
    Класс проверки отработки представлений для приложения услуг.
    """
    @classmethod
    def setUpClass(cls):
        """
        Метод установки значеений перед прогоном всех тестов, отрабатывает один раз перед
        началом всех тестов.
        """
        super().setUpClass()
        cls.marketer = User.objects.create_user(
            username="Marketer",
            password="marketerPassword",
        )
        cls.admin = User.objects.create_superuser(
            username="Admin",
            password="adminPassword",
        )
        cls.client = Client()

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
        Метод установки значений перед каждым тестом, то есть значения создаются перед каждым
        новым тестом заново.
        """
        self.product = Product.objects.create(
            name="testProduct",
            cost=100.00,
        )

    def login_marketer(self):
        """
        Метод для входа под должностью "Маркетолог", мог быть любой пользователь,
        название должности для красоты.
        """
        return self.client.login(username="Marketer", password="marketerPassword")


    def login_admin(self):
        """
        Метод входа под администратором.
        """
        return self.client.login(username="Admin", password="adminPassword")


    def test_list_view(self):
        """
        Тест проверки невозможности просмотра услуг неавторизованным пользователем.
        Возвращает код 302 и перенаправляет на страницу входа.
        """
        self.client.logout()
        response = self.client.get(reverse("products:product-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_list_view_marketer(self):
        """
        Тест проверки возможности просмотра услуг авторизованным пользователем,
        в нашем случае маркетологом.
        Возвращает код 403, так как нужны права для просмотра, после получения прав
        возвращает код 200 и переходит на страницу.
        """
        self.login_marketer()
        response = self.client.get(reverse("products:product-list"))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Product)
        permission = Permission.objects.get(content_type=content_type, codename='view_product')
        self.marketer.user_permissions.add(permission)

        response = self.client.get(reverse("products:product-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.product.name, "testProduct")
        self.assertEqual(self.product.description, "")


    def test_list_view_admin(self):
        """
        Тест проверки возможности просмотра услуг администратором.,
        возвращает код 200 и переходит на страницу, так как админу устанавливать права
        не надо.
        """
        self.login_admin()
        response = self.client.get(reverse("products:product-list"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testProduct")
        self.assertEqual(self.product.cost, 100)


    def test_detail_product(self):
        """
        Тест проверки невозможности неавторизованным пользователем посмотреть
        детали услуг. Возвращает код 302 и перенаправляет на страницу входа.
        """
        self.client.logout()
        response = self.client.get(reverse("products:product-detail", kwargs={"pk":self.product.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_detail_prod_marketer(self):
        """
        Тест проверки возможности неавторизованным пользователем посмотреть
        детали услуг. Возвращает код 403, так как для просмотра надо дать разрешение.
         После получения разрешения возвращает код 200.
        """
        self.login_marketer()
        response = self.client.get(reverse("products:product-detail", kwargs={"pk":self.product.pk}))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Product)
        permission = Permission.objects.get(content_type=content_type, codename='view_product')
        self.marketer.user_permissions.add(permission)

        response = self.client.get(reverse("products:product-detail", kwargs={"pk":self.product.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "testProduct")
        self.assertEqual(len(response.context), 2)


    def test_detail_prod_admin(self):
        """
        Тест проверки возможности админом посмотреть детали услуг. Возвращает код
        200, т.к. админ имеет все права.
        """


    def test_create_product(self):
        """
        Тест проверки невозможности создания услуги неавторизованным пользователем,
        что в принципе, логично и так, но все же. Возвращает код 302 и
        перенаправляет на страницу входа.
        """
        self.client.logout()
        data = {
            "name":"TestProd",
            "cost":120.00,
        }
        response = self.client.post(reverse("products:product-create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


    def test_create_product_marketer(self):
        """
        Тест проверки возможности создания услуги авторизованным пользователем,
        возвращает код 403 (отсутствие разрешения), при выдаче разрешения на создание услуги
        и, чтоб посмотреть результат, на просмотр, возвращается код 302 (перенаправление на список
        услуг согласно представлению).
        """
        self.login_marketer()
        data = {
            "name": "TestProd",
            "description": "qwerty",
            "cost": 120.00,
        }
        response = self.client.post(reverse("products:product-create"), data=data)
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Product)
        add_permission = Permission.objects.get(content_type=content_type, codename='add_product')
        view_permission = Permission.objects.get(content_type=content_type, codename='view_product')
        self.marketer.user_permissions.add(add_permission, view_permission)

        response = self.client.post(reverse("products:product-create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("products:product-list"))
        self.assertTrue(Product.objects.filter(name="TestProd").exists())
        new_product = Product.objects.get(name="TestProd")
        self.assertEqual(new_product.name, "TestProd")
        self.assertEqual(new_product.cost, 120.00)



    def test_create_product_admin(self):
        """
        Тест проверки возможности создания услуги администратором,
        возвращает код 302 (перенаправление на список услуг согласно представлению).
        """
        self.login_admin()
        data = {
            "name": "TestProduct",
            "description": "qwerty",
            "cost": 110.00,
        }
        response = self.client.post(reverse("products:product-create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("products:product-list"))
        self.assertTrue(Product.objects.filter(name="TestProduct").exists())
        new_product = Product.objects.get(name="TestProduct")
        self.assertEqual(new_product.name, "TestProduct")
        self.assertEqual(new_product.description, "qwerty")


    def test_update_product(self):
        """
        Тест проверки невозможности обновления услуг неавторизованным пользователем.
        Возвращает код 302 и перенаправляет на страницу входа.
        """
        self.client.logout()
        data = {
            "name": "TestProdUpdate",
            "cost": 90.00,
        }
        response = self.client.post(reverse("products:product-update", kwargs={"pk":self.product.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


    def test_update_marketer(self):
        """
        Тест возможности маркетологом создать услугу, при отсутствии прав возвращает код 403,
        при получении разрешений на обновление и просмотр услуг - 302 и перенаправляет на страницу
        услуги.
        """
        self.login_marketer()
        data = {
            "name": "TestProdUpdate",
            "cost": 90.00,
        }
        response = self.client.post(reverse("products:product-update", kwargs={"pk": self.product.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Product)
        change_permission = Permission.objects.get(content_type=content_type, codename='change_product')
        view_permission = Permission.objects.get(content_type=content_type, codename='view_product')
        self.marketer.user_permissions.add(change_permission, view_permission)

        response = self.client.post(reverse("products:product-update", kwargs={"pk": self.product.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertRedirects(response, reverse("products:product-detail", kwargs={"pk":self.product.pk}))
        self.assertTrue(Product.objects.filter(name="TestProdUpdate").exists())
        self.assertEqual(self.product.name, "TestProdUpdate")


    def test_update_admin(self):
        """
        Тест возможности админом создать услугу возвращает код  302 и перенаправляет на страницу
        услуги.
        """
        self.login_admin()
        data = {
            "name": "ProdUpdate",
            "cost": 90.00,
            "description":"qwe1"
        }
        response = self.client.post(reverse("products:product-update", kwargs={"pk": self.product.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertRedirects(response, reverse("products:product-detail", kwargs={"pk":self.product.pk}))
        self.assertEqual(self.product.description, "qwe1")


    def test_delete_prod(self):
        """
        Тест проверки невозможности неавторизованным пользователем удалить услугу.
        Возвращает код 302 и перенаправляет на страницу входа.
        """
        self.client.logout()
        response = self.client.post(reverse("products:product-delete", kwargs={"pk":self.product.pk}))
        self.assertEqual(response.status_code, 403)

    def test_delete_prod_marketer(self):
        """
        Тест проверки невозможности удаления услуги маркетологом.
        Даже при выдаче прав на удаление и просмотр возвращает код 403,
        так как в представлении заложено удаление только администратором.
        """
        self.login_marketer()
        response = self.client.post(reverse("products:product-delete", kwargs={"pk": self.product.pk}))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Product)
        delete_permission = Permission.objects.get(content_type=content_type, codename='delete_product')
        view_permission = Permission.objects.get(content_type=content_type, codename='view_product')
        self.marketer.user_permissions.add(delete_permission, view_permission)

        response = self.client.post(reverse("products:product-delete", kwargs={"pk": self.product.pk}))
        self.assertEqual(response.status_code, 403)


    def test_delete_admin(self):
        """
        Тест проверки возможности удаления услуги админом.
        Возвращает код 302 и перенаправляет на список услуг.,
        """
        self.login_admin()
        response = self.client.post(reverse("products:product-delete", kwargs={"pk": self.product.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Product.objects.filter(name="testProduct").exists())
        self.assertRedirects(response, reverse("products:product-list"))
