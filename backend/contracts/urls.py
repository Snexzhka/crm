"""
Подключение путей в приложении контрактов
"""

from django.urls import path

from .views import (
    ContractDeleteView,
    ContractListView,
    ContractsCreateView,
    ContractsDetailView,
    ContractUpdateView,
)

app_name = "contracts"

urlpatterns = [
    path("", ContractListView.as_view(), name="contracts-list"),
    path("new/", ContractsCreateView.as_view(), name="contracts_create"),
    path("<int:pk>/", ContractsDetailView.as_view(), name="contracts-detail"),
    path("<int:pk>/edit/", ContractUpdateView.as_view(), name="contract-update"),
    path("<int:pk>/delete/", ContractDeleteView.as_view(), name="contract-delete"),
]
