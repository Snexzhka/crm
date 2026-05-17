from django.contrib import admin

from .models import Contract


@admin.register(Contract)
class ContractsAdmin(admin.ModelAdmin):
    list_display = ["pk", "name", "products__name", "start_date", "cost", "lead__last_name"]

    list_display_links = ["pk", "name", "products__name",  "lead__last_name"]

    ordering = ["pk", "name", "start_date"]

    search_fields = [ "name", "products__name", "start_date", "duration",  "lead__last_name"]
