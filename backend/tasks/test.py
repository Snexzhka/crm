import datetime

import pytest
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

from .models import Task

@pytest.mark.django_db
def test_task_model(task):
    assert task.title == "TestTask"
    assert task.user.username == "TestUser"
    assert task.is_completed == False
    assert task.description == "Desc"


@pytest.mark.django_db
def test_view_task(client):
    url = reverse("tasks:tasks-list")
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_view_by_user(user, auth_user):
    url = reverse("tasks:tasks-list")
    response = auth_user.get(url)
    assert response.status_code == 200
    assert "tasks" in response.context


@pytest.mark.django_db
def test_view_by_admin(auth_admin):
    url = reverse("tasks:tasks-list")
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert "user" in response.context


@pytest.mark.django_db
def test_view_detail_task(client, task):
    url = reverse("tasks:tasks-detail", kwargs={"pk":task.pk})
    response = client.get(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_view_detail_tby_user(auth_user, task):
    url = reverse("tasks:tasks-detail", kwargs={"pk":task.pk})
    response = auth_user.get(url)
    assert response.status_code == 200
    assert Task.objects.count() == 1
    assert Task.objects.get(title="TestTask").description == "Desc"


@pytest.mark.django_db
def test_view_detail_tby_admin(auth_admin, task):
    url = reverse("tasks:tasks-detail", kwargs={"pk":task.pk})
    response = auth_admin.get(url)
    assert response.status_code == 200
    assert Task.objects.count() == 1
    assert Task.objects.get(title="TestTask").description == "Desc"


@pytest.mark.django_db
def test_create_task(client, task, user):
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
    url = reverse("tasks:tasks-delete", kwargs={"pk":task.pk})
    response = client.post(url)
    assert response.status_code == 302
    assert "login" in response.url


@pytest.mark.django_db
def test_delete_by_user(auth_user, task):
    url = reverse("tasks:tasks-delete", kwargs={"pk":task.pk})
    response = auth_user.post(url)
    assert response.status_code == 302
    assert not Task.objects.filter(title="TestTask").exists()
    assert Task.objects.count() == 0


@pytest.mark.django_db
def test_delete_by_admin(auth_admin, task):
    url = reverse("tasks:tasks-delete", kwargs={"pk":task.pk})
    response = auth_admin.post(url)
    assert response.status_code == 302
    assert not Task.objects.filter(title="TestTask").exists()
    assert Task.objects.count() == 0
