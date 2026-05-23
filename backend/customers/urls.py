"""
Подключение ссылок для работы приложения
"""
from django.urls import path

from .views import (
    CustomerListView,
    CustomerCreateView,
    CustomerDeleteView,
    CustomerDetailView,
    CustomerUpdateView,

)

app_name = "customers"

urlpatterns = [
    path("", CustomerListView.as_view(), name="customers-list"),
    path("new/", CustomerCreateView.as_view(), name="customers-create"),
    path("<int:pk>/", CustomerDetailView.as_view(), name="customers-detail"),
    path("<int:pk>/edit/", CustomerUpdateView.as_view(), name="customer_update"),
    path("<int:pk>/delete/", CustomerDeleteView.as_view(), name="customer-delete"),

    ]
