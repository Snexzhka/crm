from django.contrib import admin
from django.urls import path, include

from .views import (
    LeadListView,
    LeadDetailView,
    LeadsCreateView,
    LeadUpdateView,
    LeadDeleteView,
    ConvertLeadView,

)

app_name = "leads"

urlpatterns = [
    path("", LeadListView.as_view(), name="leads-list"),
    path("<int:pk>/", LeadDetailView.as_view(), name="leads-detail"),
    path("new/", LeadsCreateView.as_view(), name="leads-create"),
    path("<int:pk>/edit/", LeadUpdateView.as_view(), name="leads-update"),
    path("<int:pk>/delete/", LeadDeleteView.as_view(), name="leads-delete"),
    path("<int:pk>/converts/", ConvertLeadView.as_view(), name="leads-convert"),

    ]