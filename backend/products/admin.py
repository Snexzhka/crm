"""
Подключение модели в административной панели
"""
from django.contrib import admin

from .models import Product


@admin.register(Product)
class ProductsAdmin(admin.ModelAdmin):
    """
    Определены поля, отражаемые в админ панели, ссылки для
    быстрого перехода, поля для сортировки и поиска.
    """


    list_display = ["pk", "name", "description", "cost"]

    list_display_links = ["pk", "name"]

    ordering = ["pk", "name"]

    search_fields = ["pk", "name", "cost"]
