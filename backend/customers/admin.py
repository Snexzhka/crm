"""
Подключение приложения в админ панели
"""

from django.contrib import admin

from .models import Customer


@admin.register(Customer)
class CustomersAdmin(admin.ModelAdmin):
    """
    Класс, определяющий список полей для формы и
    отражаемые активные ссылки по полям, поля поиска
    и сортировку.
    """

    list_display = ["pk", "lead__last_name", "contract__name"]

    list_display_links = ["pk", "lead__last_name", "contract__name"]

    ordering = ("pk", "lead__last_name")

    search_fields = ["pk", "lead__last_name", "contract__name"]
