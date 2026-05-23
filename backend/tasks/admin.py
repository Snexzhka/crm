"""
Подключение приложения к административной панели
"""

from django.contrib import admin

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    """
    Определены необходимые доя отображения поля, ссылки для быстрого
    перехода, поля для поиска и сортировки
    """

    list_display = [
        "pk",
        "title",
        "created_at",
        "due_date",
        "is_completed",
        "user",
    ]

    list_display_links = ["pk", "title"]

    ordering = ["pk", "title", "user"]

    search_fields = ("title", "is_completed", "user")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(user=request.user)
