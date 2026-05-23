"""
Тестирование на основе TestCase
"""

import os
import shutil

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.urls import reverse
from django.conf import settings
from django.utils import timezone

from .models import Task

User = get_user_model()


class TaskModelTest(TestCase):
    """
    Класс проверки создания объектов текущих задач.
    """

    def setUp(self):
        """
        Метод создания данных для тестов, создает данные каждый раз перед началом
        каждого теста.
        """

        self.user = User.objects.create_user(username="testUser", password="111")

    def test_create_task(self):
        """
        Тест проверки создания моделей задач.
        """

        task = Task.objects.create(
            user=self.user,
            title="task1",
            description="task_for_you",
            due_date=timezone.now().date(),
        )

        self.assertEqual(task.title, "task1")
        self.assertEqual(task.user, self.user)
        self.assertEqual(task.description, "task_for_you")
        self.assertFalse(task.is_completed)
        self.assertTrue(str(task.title))
        self.assertTrue(Task.objects.filter(title="task1"))


class TaskViewTest(TestCase):
    """
    Класс проверки работы представлений.
    """

    @classmethod
    def setUpClass(cls):
        """
        Метод создания данных для тестов - создают данные один раз перед
        прогоном всех тестов. Экономит ресурсы, создаются данные, которые
        в тестах не меняются.
        """
        super().setUpClass()
        cls.client = Client()
        cls.user = User.objects.create_user(
            username="testUser", password="testPassword"
        )
        cls.admin = User.objects.create_superuser(
            username="admin", password="adminPassword"
        )

    @classmethod
    def tearDownClass(cls):
        """
        Метод для подтирания медиа файлов после прогона всех тестов. Запускается в конце,
        после отработки всех тестов.
        """

        # Проверяем, существует ли переопределённая настройка
        if hasattr(cls, "_overridden_settings") and cls._overridden_settings:
            media_root = cls._overridden_settings.get("MEDIA_ROOT")
            if media_root and os.path.exists(media_root):
                shutil.rmtree(media_root, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        """
        Метод создания данных перед каждым тестом заново. Создает объект задачи, так как он
        может меняться после каждого теста.
        """

        self.task = Task.objects.create(
            user=self.user,
            title="task1",
            description="task_for_you",
            due_date=timezone.now().date(),
        )

    def login_user(self):
        """
        Метод, позволяющий войти под авторизованным пользователем.
        """

        return self.client.login(username="testUser", password="testPassword")

    def login_admin(self):
        """
        Метод, позволяющий войти под админом.
        """

        return self.client.login(username="admin", password="adminPassword")

    def test_list_view_without_login(self):
        """
        Тест проверки возможности просмотреть список задач без авторизации.
        Возвращает код 302 (переадресация на login).
        """

        self.client.logout()
        response = self.client.get(reverse("tasks:tasks-list"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_list_view(self):
        """
        Тест проверки возможности просмотреть список задач после авторизации.
        Возвращает код 200.
        """

        self.login_user()
        response = self.client.get(reverse("tasks:tasks-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(type(response.context), list)
        self.assertEqual(len(response.context), 2)
        self.assertTrue(type(response.context), list)

    def test_list_view_admin(self):
        """
        Тест проверки возможности просмотреть список задач админом.
        Возвращает код 200.
        """

        self.login_admin()
        response = self.client.get(reverse("tasks:tasks-list"))
        self.assertEqual(response.status_code, 200)

    def test_detail_task_view(self):
        """
        Тест проверки просмотра деталей конкретной задачи без авторизации.
        Возвращает код 302.
        """

        self.client.logout()
        response = self.client.get(
            reverse("tasks:tasks-detail", kwargs={"pk": self.task.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_task_detail(self):
        """
        Тест проверки просмотра деталей конкретной задачи после авторизации.
        Возвращает код 200.
        """

        self.login_user()
        response = self.client.get(
            reverse("tasks:tasks-detail", kwargs={"pk": self.task.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context), 2)
        self.assertContains(response, "task1")
        self.assertContains(response, "testUser")

    def test_task_detail_admin(self):
        """
        Тест проверки просмотра деталей конкретной задачи админом.
        Возвращает код 200.
        """
        self.login_admin()
        response = self.client.get(
            reverse("tasks:tasks-detail", kwargs={"pk": self.task.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.task.title, "task1")

    def test_task_create_view(self):
        """
        Тест создания объекта задачи без авторизации пользователя (и без прав на
        создание, соответственно). Возвращает код 403.
        """
        self.client.logout()
        data = {
            "user": self.user.pk,
            "title": "task2",
            "description": "Desc",
            "due_date": "2026-12-31",
        }
        response = self.client.post(reverse("tasks:tasks-create"), data=data)
        self.assertEqual(response.status_code, 403)

    def test_create_task_user(self):
        """
        Тест создания объекта задачи без прав на создание. Возвращает код 403.
        После получения прав объект задачи создается, код возврата 302
        (перенаправление на список задач). Проверяется существование вновь
         созданной задачи.
        """
        self.login_user()
        data = {
            "user": self.user.pk,
            "title": "task2",
            "description": "Desc",
            "due_date": "2026-12-31",
        }
        response = self.client.post(reverse("tasks:tasks-create"), data=data)
        self.assertEqual(response.status_code, 403)

        content_type = ContentType.objects.get_for_model(Task)
        permission = Permission.objects.get(
            content_type=content_type, codename="add_task"
        )
        self.user.user_permissions.add(permission)

        response = self.client.post(reverse("tasks:tasks-create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title="task2").exists())
        new_task = Task.objects.get(title="task2")
        self.assertEqual(new_task.description, "Desc")
        self.assertRedirects(response, reverse("tasks:tasks-list"))

    def test_create_task_by_admin(self):
        """
        Тест создания объекта задачи админом. Возвращает код 302 (перенаправление
        на список задач). Проверяется существование вновь созданной задачи.
        Админу не требуется предоставление дополнительных прав.
        """
        self.login_admin()
        data = {
            "user": self.user.pk,
            "title": "task3",
            "description": "Desc",
            "due_date": "2026-12-31",
        }
        response = self.client.post(reverse("tasks:tasks-create"), data=data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tasks:tasks-list"))
        new_task = Task.objects.get(title="task3")
        self.assertEqual(new_task.description, "Desc")
        self.assertTrue(Task.objects.filter(title="task3").exists())
        self.assertRedirects(response, reverse("tasks:tasks-list"))

    def test_update_task_without_login(self):
        """
        Тест проверки обновления объекта задачи без авторизации.
        Возвращает код 302 (перенаправляет на логин).
        """
        self.client.logout()
        data = {
            "title": "task3",
            "description": "Desc",
            "due_date": "2026-12-31",
        }
        response = self.client.post(
            reverse("tasks:tasks-update", kwargs={"pk": self.task.pk}),
            data=data,
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotEqual(self.task.description, "Desc")
        self.assertNotEqual(self.task.title, "task3")
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_update_task_by_user(self):
        """
        Тест проверки обновления объекта задачи после авторизации.
        Возвращает код 302 (перенаправляет страницу задачи).
        Проверяется обновление определенных полей и адрес перенаправления.
        """

        data = {
            "title": "task3",
            "description": "Desc1",
            "due_date": "2026-12-31",
        }
        self.login_user()
        response = self.client.post(
            reverse("tasks:tasks-update", kwargs={"pk": self.task.pk}),
            data=data,
        )
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertEqual(self.task.title, "task3")
        self.assertEqual(self.task.description, "Desc1")
        self.assertRedirects(
            response, reverse("tasks:tasks-detail", kwargs={"pk": self.task.pk})
        )

    def test_update_task_admin(self):
        """
        Тест проверки обновления объекта задачи админом.
        Возвращает код 302 (перенаправляет страницу задачи).
        Проверяется обновление определенных полей и адрес перенаправления.
        """
        data = {
            "title": "task4",
            "description": "Desc2",
            "due_date": "2026-12-31",
        }
        self.login_admin()
        response = self.client.post(
            reverse("tasks:tasks-update", kwargs={"pk": self.task.pk}),
            data=data,
        )
        self.assertEqual(response.status_code, 302)
        self.task.refresh_from_db()
        self.assertNotEqual(self.task.title, "task3")
        self.assertEqual(self.task.description, "Desc2")
        self.assertRedirects(
            response, reverse("tasks:tasks-detail", kwargs={"pk": self.task.pk})
        )

    def test_delete_task_without_login(self):
        """
        Тест проверки невозможности удаления задачи без авторизации.
        Возвращает код 302 (перенаправляет на страницу авторизации).
        """

        self.client.logout()
        response = self.client.post(
            reverse("tasks:tasks-delete", kwargs={"pk": self.task.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Task.objects.filter(title=self.task.title).exists())
        self.assertIn(str(settings.LOGIN_URL), response.url)

    def test_delete_task(self):
        """
        Тест проверки возможность удаления задачи после авторизации и
        получения соответствующих прав. Возвращает код 302 (перенаправление
        на список задач).
        """
        self.login_user()
        content_type = ContentType.objects.get_for_model(Task)
        permission = Permission.objects.get(
            content_type=content_type, codename="delete_task"
        )
        self.user.user_permissions.add(permission)
        response = self.client.post(
            reverse("tasks:tasks-delete", kwargs={"pk": self.task.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tasks:tasks-list"))
        self.assertFalse(Task.objects.filter(pk=self.task.pk).exists())

    def test_admin_delete_task(self):
        """
        Тест проверки возможность удаления задачи админом (получение дополнительных
         прав не требуется). Возвращает код 302 (перенаправление на список задач).
        """

        self.login_admin()
        response = self.client.post(
            reverse("tasks:tasks-delete", kwargs={"pk": self.task.pk})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("tasks:tasks-list"))
        self.assertFalse(Task.objects.filter(title="task1").exists())
