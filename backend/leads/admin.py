"""
Подключение модели потенциальных клиентов к административной
панели
"""
from django.contrib import admin

from .models import Lead


@admin.register(Lead)
class LeadsAdmin(admin.ModelAdmin):
    """
    Определены поля, отражаемые в админ панели, ссылки, поля для
    поиска и сортировки
    """
    list_display = ["pk", "first_name", "last_name", "phone", "email", "advert_name__name"]

    list_display_links = ["pk",  "last_name", "advert_name__name"]

    ordering = ("pk", "last_name")

    search_fields = ["first_name", "last_name", "phone", "email"]
