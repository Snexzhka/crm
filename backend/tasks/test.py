import datetime

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import Task

@pytest.mark.django_db
def test_task_model(task):
    """
    Тест проверки создания объектов моделей задач
    :param task: fixture
    """
    assert task.title == "TestTask"
    assert task.user.username == "TestUser"
    assert task.is_completed == False
    assert task.description == "Desc"


@pytest.mark.django_db
def test_view_task(client):
    """
    Тест проверки невозможности просмотра списка задач неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param client: fixture
    :return: 302
    """
    url = reverse("tasks:tasks-list")
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_view_by_user(user, auth_user):
    """
    Тест проверки возможности просмотра списка задач авторизованным пользователем.
    Возвращает код 200. Согласно представлению дополнительные разрешения не нужны.
    :param client: fixture
    :return: 200
    """
    url = reverse("tasks:tasks-list")
    response = auth_user.get(url)
    assert response.status_code == 200
    assert "tasks" in response.context


@pytest.mark.django_db
def test_view_by_admin(auth_admin):
    """
    Тест проверки возможности просмотра списка задач администратором.
    Возвращает код 200.
    :param client: fixture
    :return: 200
    """
    url = reverse("tasks:tasks-list")
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert "user" in response.context


@pytest.mark.django_db
def test_view_detail_task(client, task):
    """
    Тест проверки невозможности просмотра деталей задач неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param client: fixture
    :return: 302
    """
    url = reverse("tasks:tasks-detail", kwargs={"pk":task.pk})
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_view_detail_by_user(auth_user, task):
    """
    Тест проверки возможности просмотра деталей задач авторизованным пользователем.
    Возвращает код 200. Согласно представлению дополнительные разрешения не нужны.
    :param client: fixture
    :return: 200
    """
    url = reverse("tasks:tasks-detail", kwargs={"pk":task.pk})
    response = auth_user.get(url)
    assert response.status_code == 200
    assert Task.objects.count() == 1
    assert Task.objects.get(title="TestTask").description == "Desc"


@pytest.mark.django_db
def test_view_detail_by_admin(auth_admin, task):
    """
    Тест проверки возможности просмотра деталей задач администратором.
    Возвращает код 200.
    :param client: fixture
    :return: 200
    """
    url = reverse("tasks:tasks-detail", kwargs={"pk":task.pk})
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert Task.objects.count() == 1
    assert Task.objects.get(title="TestTask").description == "Desc"


@pytest.mark.django_db
def test_create_task(client, task, user):
    """
    Тест проверки невозможности создания новой задачи неавторизованным пользователем.
    Возвращает код 403.
    :param client: fixture
    :param task: fixture
    :param user: fixture
    :return: 403
    """
    data = {
        "user":user,
        "title":"NewTask",
        "description":"NewDesc",
        "due_date":"2026-12-31",
    }
    url = reverse("tasks:tasks-create")
    response = client.post(url,data)
    assert response.status_code== 403


@pytest.mark.django_db
def test_create_by_user(auth_user, user, task):
    """
    Тест проверки возможности создания новой задачи авторизованным пользователем.
    Создает задачу и возвращает код 302 при наличии определенных прав.
    :param client: fixture
    :param task: fixture
    :param user: fixture
    :return: 302
    """
    data = {
        "user": user.pk,
        "title": "NewTask",
        "description": "NewDesc",
        "due_date": "2026-12-31",
    }
    url = reverse("tasks:tasks-create")
    response = auth_user.post(url, data)
    assert response.status_code == 403

    content_type = ContentType.objects.get_for_model(Task)
    add_permission = Permission.objects.get(content_type=content_type, codename='add_task')
    user.user_permissions.add(add_permission)

    response = auth_user.post(url, data)
    assert response.status_code == 302
    assert Task.objects.count() == 2
    assert Task.objects.filter(title="NewTask").exists()
    assert Task.objects.get(title="NewTask").description == "NewDesc"


@pytest.mark.django_db
def test_create_by_admin(auth_admin, user_admin, task):
    """
    Тест проверки возможности создания новой задачи администратором.
    Создает задачу и возвращает код 302.
    :param client: fixture
    :param task: fixture
    :param user: fixture
    :return: 302
    """
    data = {
        "user": user_admin.pk,
        "title": "NewTask",
        "description": "NewDesc",
        "due_date": "2026-12-31",
    }
    url = reverse("tasks:tasks-create")
    response = auth_admin.post(url, data)
    assert response.status_code == 302
    assert Task.objects.count() == 2
    assert Task.objects.filter(title="NewTask").exists()
    assert Task.objects.get(title="NewTask").description == "NewDesc"


@pytest.mark.django_db
def test_update_task(client, task, user):
    """
    Тест проверки невозможности обновления задачи неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param client: fixture
    :param task: fixture
    :param user: fixture
    :return: 302
    """
    data = {
        "user":user,
        "title":"UpdateTask",
        "description":"UpdateDesc",
        "due_date":"2026-12-31",
    }
    url = reverse("tasks:tasks-update", kwargs={"pk":task.pk})
    response = client.post(url,data)
    assert response.status_code== 302
    assert "login" in response.url


@pytest.mark.django_db
def test_update_by_user(auth_user, task, user):
    """
    Тест проверки возможности обновления задачи авторизованным пользователем.
    Обновляет поля задачи и возвращает код 302.
    :param client: fixture
    :param task: fixture
    :param user: fixture
    :return: 302
    """
    data = {
        "user":user,
        "title":"UpdateTask",
        "description":"UpdateDesc",
        "due_date":"2026-12-31",
    }
    url = reverse("tasks:tasks-update", kwargs={"pk":task.pk})
    response = auth_user.post(url,data)
    assert response.status_code == 302
    assert Task.objects.get(title="UpdateTask").description == "UpdateDesc"
    assert Task.objects.filter(title="UpdateTask").exists()


@pytest.mark.django_db
def test_update_by_admin(auth_admin, task, user):
    """
    Тест проверки возможности обновления задачи администратором.
    Обновляет задачу и возвращает код 302.
    :param client: fixture
    :param task: fixture
    :param user: fixture
    :return: 302
    """
    data = {
        "user":user,
        "title":"UpdateTask",
        "description":"UpdateDesc",
        "due_date":"2026-12-31",
    }
    url = reverse("tasks:tasks-update", kwargs={"pk":task.pk})
    response = auth_admin.post(url,data)
    assert response.status_code== 302
    assert Task.objects.get(title="UpdateTask").description == "UpdateDesc"
    assert Task.objects.filter(title="UpdateTask").exists()


@pytest.mark.django_db
def test_delete_task(client, task):
    """
    Тест проверки невозможности удаления задачи неавторизованным пользователем.
    Возвращает код 302 и направляет на страницу входа.
    :param client: fixture
    :param task: fixture
    :param user: fixture
    :return: 302
    """
    url = reverse("tasks:tasks-delete", kwargs={"pk":task.pk})
    response = client.post(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_delete_by_user(auth_user, task):
    """
    Тест проверки возможности удаления задачи авторизованным пользователем.
    Удаляет задачу и возвращает код 302.
    :param client: fixture
    :param task: fixture
    :param user: fixture
    :return: 302
    """
    url = reverse("tasks:tasks-delete", kwargs={"pk":task.pk})
    response = auth_user.post(url)
    assert response.status_code == 302
    assert not Task.objects.filter(title="TestTask").exists()
    assert Task.objects.count() == 0


@pytest.mark.django_db
def test_delete_by_admin(auth_admin, task):
    """
    Тест проверки возможности удаления задачи администратором.
    Удаляет задачу и возвращает код 302.
    :param client: fixture
    :param task: fixture
    :param user: fixture
    :return: 302
    """
    url = reverse("tasks:tasks-delete", kwargs={"pk":task.pk})
    response = auth_admin.post(url)
    assert response.status_code == 302
    assert not Task.objects.filter(title="TestTask").exists()
    assert Task.objects.count() == 0
