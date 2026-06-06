"""
Представление приложения в админ панели
"""

from django.contrib import admin

from .models import Contract


@admin.register(Contract)
class ContractsAdmin(admin.ModelAdmin):
    """
    Класс для определения полей и ссылок в админ панели.
    """

    list_display = [
        "pk",
        "name",
        "products__name",
        "start_date",
        "cost",
        "lead__last_name",
    ]

    list_display_links = ["pk", "name", "products__name", "lead__last_name"]

    ordering = ["pk", "name", "start_date"]

    search_fields = [
        "name",
        "products__name",
        "start_date",
        "duration",
        "lead__last_name",
    ]

    fieldsets = (
        (None, {
            "fields": ("name", "products", "duration", "cost", "lead", "file"),
            "help_texts": {
                "duration": "Введите продолжительность в формате: '5 days', '1 day 12 hours'",
            }
        }),
    )
