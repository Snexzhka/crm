"""
Модель для определения пользователей приложения
"""

from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Profile(models.Model):
    """
    Модель пользователей. Определяет профессию и отдел,
    имеет связь с таблицей User
    Поля:
        job_title:профессия
        department:отдел
        user:связь с таблицей User
    """

    class Meta:
        ordering = ["pk", "user"]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    job_title: models.CharField = models.CharField(max_length=200)
    department: models.CharField = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.user}  {self.job_title} {self.department}"
