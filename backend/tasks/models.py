"""
Модель для приложения текущих задач
"""

from django.db import models
from django.conf import settings
from django.utils import timezone


class Task(models.Model):
    """
    Модель для текущих задач. Содержит данные и названии задачи, ее
    описание, даты внесения задачи в ежедневник и срок исполнения,
    отметку о выполнении, связь с пользователем, ее создавшим.
    Поля:
        user:связь с исполнителем
        title:название задачи
        description:описание задачи
        due_date:дата внесения задачи (начало исполнения)
        is_completed:отметка о выполнении
        created_at: исполнить до (срок исполнения)
    """

    class Meta:
        ordering = ["title", "due_date", "-created_at"]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tasks"
    )
    title: models.CharField = models.CharField(max_length=250)
    description: models.TextField = models.TextField(null=True, blank=True)
    due_date: models.DateField = models.DateField(default=timezone.now)
    is_completed: models.BooleanField = models.BooleanField(default=False)
    created_at: models.DateTimeField = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title}, {self.description} : {self.due_date}"
