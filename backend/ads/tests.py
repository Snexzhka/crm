import os
import shutil

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client
from django.contrib.auth.models import User, Permission
from django.urls import reverse
from django.utils import timezone

from .models import Advert
from products.models import Product


class AdvertModelTest(TestCase):

    def test_model_ads(self):
        self.product = Product.objects.create(
            name="testProd",
            description="qwerty",
            cost=100,
        )

        self.ads = Advert.objects.create(
            name="testAdvert",
            products=self.product,
            promotion_path="internet",
            budget=79,
        )

        self.assertEqual(self.ads.name, "testAdvert")
        self.assertEqual(self.ads.products.pk, self.product.pk)
        self.assertNotEqual(self.ads.promotion_path, "newspaper")
        self.assertEqual(self.ads.budget, 79)


class AdvertTestView(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.marketer = User.objects.create_user(
            username="Marketer",
            password="marketerPassword",
        )
        cls.admin = User.objects.create_superuser(
            username="Admin",
            password="adminPassword",
        )
        cls.product = Product.objects.create(
            name="testProduct",
            description="qwerty",
            cost=100.00,
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
        self.ads = Advert.objects.create(
            name="testAdvert",
            products=self.product,
            promotion_path="internet",
            budget=79,
        )

    def login_marketer(self):
        return self.client.login(username="Marketer", password="marketerPassword")


    def login_admin(self):
        return self.client.login(username="Admin", password="adminPassword")


    def test_list_view(self):
        self.client.logout()
        response = self.client.get(reverse("ads:ads-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


    def test_list_view_marketer(self):
        self.login_marketer()
        response = self.client.get(reverse("ads:ads-list"))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Advert)
        permission = Permission.objects.get(content_type=content_type, codename='view_advert')
        self.marketer.user_permissions.add(permission)

        response = self.client.get(reverse("ads:ads-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ads.name, "testAdvert")


    def test_list_view_admin(self):
        self.login_admin()
        response = self.client.get(reverse("ads:ads-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ads.budget, 79)
