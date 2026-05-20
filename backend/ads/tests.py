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
    """
    Класс проверки создания объектов модели рекламных компаний.
    """
    def test_model_ads(self):
        """
        Тест проверки создания объектов модели
        """
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
    """
    Класс проверки работы представлений рекламных компаний
    """
    @classmethod
    def setUpClass(cls):
        """
        Метод установки данных для тестов, отрабатывает один раз перед прогоном всех тестов,
        в самом начале.
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
        """
        Класс установки данных для тестов, данные устанавливаются заново перед каждым тестом
        """
        self.ads = Advert.objects.create(
            name="testAdvert",
            products=self.product,
            promotion_path="internet",
            budget=79,
        )

    def login_marketer(self):
        """
        Метод для входа под именем маркетолога. Мог быть любой пользователь,
        "маркетолог" для красоты согласно ТЗ
        """
        return self.client.login(username="Marketer", password="marketerPassword")


    def login_admin(self):
        """
        Метод для входа под админом
        """
        return self.client.login(username="Admin", password="adminPassword")


    def test_list_view(self):
        """
        Тест проверки невозможности просмотра списка рекламных компаний
        без авторизации. Возвращает код 302, проверяется перенаправление
        на страницу входа.
        """
        self.client.logout()
        response = self.client.get(reverse("ads:ads-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)


    def test_list_view_marketer(self):
        """
        Тест проверки невозможности просмотра списка рекламных компаний
        авторизованным пользователем. Сначала возвращает код 403 (отсутствие прав), после
        наделения правами - код 200.
        """
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
        """
        Тест проверки невозможности просмотра списка рекламных компаний
        администратором. Возвращает код 200, так как админу
        права не нужны.
        """
        self.login_admin()
        response = self.client.get(reverse("ads:ads-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ads.budget, 79)


    def test_detail_view(self):
        """
        Тест проверки невозможности неавторизованным пользователем
        просмотреть детали отдельно взятой рекламной компании.
        Возвращает код 302 (происходит перенаправление на страницу входа).
        """
        self.client.logout()
        response = self.client.get(reverse("ads:ads-detail", kwargs={"pk":self.ads.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_detail_marketer(self):
        """
        Тест проверки входа авторизованным пользователем на страницу просмотра
        деталей рекламной компании. Сначала, при отсутствии прав просмотра,
        возвращает код 403, после наделения правами - 200.
        """
        self.login_marketer()
        response = self.client.get(reverse("ads:ads-detail", kwargs={"pk":self.ads.pk}))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Advert)
        permission = Permission.objects.get(content_type=content_type, codename='view_advert')
        self.marketer.user_permissions.add(permission)

        response = self.client.get(reverse("ads:ads-detail", kwargs={"pk": self.ads.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ads.name, "testAdvert")
        self.assertContains(response, 79)


    def test_detail_admin(self):
        """
        Тест просмотра деталей рекламной компании админом. Возвращает код 200.
        """
        self.login_admin()
        response = self.client.get(reverse("ads:ads-detail", kwargs={"pk": self.ads.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.ads.budget, 79)
        self.assertContains(response, "testAdvert")


    def test_create_ads(self):
        """
        Тест для подтверждения невозможности создания объекта рекламной компании
        неавторизованным пользователем. Возвращает код 302 с перенаправлением
        на страницу входа.
        """
        self.client.logout()
        data = {
            "name": "testAds",
            "products":self.product.pk,
            "promotion_path": "newspaper",
            "budget":150.00,
        }
        response = self.client.post(reverse("ads:ads-create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_create_marketer(self):
        """
        Тест проверки создания рекламной компании авторизованным пользователем.
        При отсутствии прав возвращает код 403, после наделения правами - 302 с
        перенаправлением на страницу списка рекламных компаний.
        """
        self.login_marketer()
        data = {
            "name": "testAds",
            "products": self.product.pk,
            "promotion_path": "newspaper",
            "budget": 150.00,
        }
        response = self.client.post(reverse("ads:ads-create"), data=data)
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Advert)
        add_permission = Permission.objects.get(content_type=content_type, codename='add_advert')
        view_permission = Permission.objects.get(content_type=content_type, codename='view_advert')
        self.marketer.user_permissions.add(add_permission, view_permission)

        response = self.client.post(reverse("ads:ads-create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("ads:ads-list"))
        self.assertTrue(Advert.objects.filter(name="testAds").exists())
        self.assertEqual(Advert.objects.count(), 2)
        new_ads = Advert.objects.get(name="testAds")
        self.assertNotEqual(new_ads.promotion_path, "testAds")


    def test_create_admin(self):
        """
        Тест проверки создания рекламной компании администратором.
        Возвращает код 302 с перенаправлением на страницу списка рекламных компаний.
        """
        self.login_admin()
        data = {
            "name": "testAds",
            "products": self.product.pk,
            "promotion_path": "newspaper",
            "budget": 150.00,
        }
        response = self.client.post(reverse("ads:ads-create"), data=data)
        self.assertTrue(Advert.objects.filter(pk=2).exists())
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("ads:ads-list"))
        self.assertEqual(Advert.objects.count(), 2)

        new_ads = Advert.objects.get(name="testAds")
        self.assertEqual(new_ads.promotion_path, "newspaper")


    def test_update_ads(self):
        """
        Тест невозможности обновления рекламной компании неавторизованным пользователем.
        Возвращает код 302 с перенаправлением на страницу входа.
        """
        self.client.logout()
        data = {
            "name": "testAds2",
            "products": self.product.pk,
            "promotion_path": "news",
            "budget": 100.00,}

        response = self.client.post(reverse("ads:ads-update", kwargs={"pk":self.ads.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_update_marketer(self):
        """
        Тест проверки возможности обновления рекламной компании авторизованным пользователем.
        Сначала, при условии отсутствия прав возвращается код 403, после наделения ими -
        302 с перенаправлением на страницу деталей рекламной компании.
        """
        self.login_marketer()
        data = {
            "name": "testAds2",
            "products": self.product.pk,
            "promotion_path": "news",
            "budget": 100.00,
        }

        response = self.client.post(reverse("ads:ads-update", kwargs={"pk": self.ads.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Advert)
        change_permission = Permission.objects.get(content_type=content_type, codename='change_advert')
        view_permission = Permission.objects.get(content_type=content_type, codename='view_advert')
        self.marketer.user_permissions.add(change_permission, view_permission)

        response = self.client.post(reverse("ads:ads-update", kwargs={"pk": self.ads.pk}),
                                    data=data)
        self.product.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("ads:ads-detail", kwargs={"pk":self.ads.pk}))
        self.assertTrue(Advert.objects.filter(name="testAds2").exists())
        update_ads = Advert.objects.get(pk=1)
        self.assertEqual(update_ads.name, "testAds2")
        self.assertEqual(update_ads.pk, 1)


    def test_update_admin(self):
        """
        Тест проверки возможности обновления рекламной компании админом.
        Возвращает код 302 с перенаправлением на страницу деталей рекламной
        компании.
        """
        self.login_admin()
        data = {
            "name": "testAds3",
            "products": self.product.pk,
            "promotion_path": "news",
            "budget": 100, }

        response = self.client.post(reverse("ads:ads-update", kwargs={"pk": self.ads.pk}),
                                    data=data)
        self.assertEqual(response.status_code, 302)
        self.product.refresh_from_db()
        self.assertRedirects(response, reverse("ads:ads-detail", kwargs={"pk": self.ads.pk}))
        self.assertTrue(Advert.objects.filter(name="testAds3").exists())
        update_ads = Advert.objects.get(pk=1)
        self.assertEqual(update_ads.promotion_path, "news")


    def test_delete_ads(self):
        """
        Тест проверки невозможности удаления рекламной компании неавторизованным пользователем.
        Возвращает код 403.
        """
        self.client.logout()
        response = self.client.post(reverse("ads:ads_delete", kwargs={"pk":self.ads.pk}))
        self.assertEqual(response.status_code, 403)


    def test_delete_marketer(self):
        """
        Тест удаления рекламной компании авторизованным пользователем.
        Возвращает код 403, даже при наличии прав, так как по условиям представления
        удалить может только админ.
        """
        self.login_marketer()
        response = self.client.post(reverse("ads:ads_delete", kwargs={"pk": self.ads.pk}))
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Advert)
        delete_permission = Permission.objects.get(content_type=content_type, codename='delete_advert')
        view_permission = Permission.objects.get(content_type=content_type, codename='view_advert')
        self.marketer.user_permissions.add(delete_permission, view_permission)

        response = self.client.post(reverse("ads:ads_delete", kwargs={"pk": self.ads.pk}))
        self.assertEqual(response.status_code, 403)


    def test_delete_admin(self):
        """
        Тест проверки удаления рекламной компании админом. Возвращает код 302 с
        перенаправлением на список рекламных компаний.
        """
        self.login_admin()
        response = self.client.post(reverse("ads:ads_delete", kwargs={"pk": self.ads.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("ads:ads-list"))
        self.assertFalse(Advert.objects.filter(name="testAdvert").exists())
