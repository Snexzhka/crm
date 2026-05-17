from django.contrib import admin
from django.urls import path, include

from .views import (
    ContractListView,
    ContractsDetailView,
    ContractsCreateView,
    ContractUpdateView,
    ContractDeleteView,
)

app_name = "contracts"

urlpatterns = [
    path("", ContractListView.as_view(), name="contracts-list"),
    path("new/", ContractsCreateView.as_view(), name="contracts_create"),
    path("<int:pk>/", ContractsDetailView.as_view(), name="contracts-detail"),
    path("<int:pk>/edit/", ContractUpdateView.as_view(), name="contract-update"),
    path("<int:pk>/delete/", ContractDeleteView.as_view(), name="contract-delete"),

    ]