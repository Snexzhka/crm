"""
Подключение админ панели для приложения
"""
from django.contrib import admin

from .models import Advert

@admin.register(Advert)
class AdvertAdmin(admin.ModelAdmin):
    """
    Класс отображения необходимых для работы полей и ссылок для быстрого перехода
    """
    list_display = ["pk", "name", "promotion_path", "budget", "products__name"]

    list_display_links = ["pk", "name", "products__name"]

    ordering = ["pk", "name"]

    search_fields = ("name", "products__name")
