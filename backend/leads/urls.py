"""
подключение ссылок приложения "leads"
"""

from django.urls import path

from .views import (
    ConvertLeadView,
    LeadDeleteView,
    LeadDeleteWithCustomerView,
    LeadDetailView,
    LeadListView,
    LeadsCreateView,
    LeadUpdateView,
)

app_name = "leads"

urlpatterns = [
    path("", LeadListView.as_view(), name="leads-list"),
    path("<int:pk>/", LeadDetailView.as_view(), name="leads-detail"),
    path("new/", LeadsCreateView.as_view(), name="leads-create"),
    path("<int:pk>/edit/", LeadUpdateView.as_view(), name="leads-update"),
    path("<int:pk>/delete/", LeadDeleteView.as_view(), name="leads-delete"),
    path("<int:pk>/converts/", ConvertLeadView.as_view(), name="leads-convert"),
    path(
        "<int:pk>/delete-with-customer/",
        LeadDeleteWithCustomerView.as_view(),
        name="delete-with-customer",
    ),
]
