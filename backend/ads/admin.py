from django.contrib import admin

from .models import Advert

@admin.register(Advert)
class AdvertAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "promotion_path", "budget", "products__name"]

    list_display_links = ["pk", "name", "products__name"]

    ordering = ["pk", "name"]

    search_fields = ("name", "products__name")
