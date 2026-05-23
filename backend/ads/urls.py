"""
Подключение путей (ссылок) для работы приложения
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AdStatisticsView,
    AdventCreateView,
    AdventDeleteView,
    AdventDetail,
    AdventView,
    AdvertUpdateView,
)

app_name = "ads"

routers = DefaultRouter()

urlpatterns = [
    path("", AdventView.as_view(), name="ads-list"),
    path("new/", AdventCreateView.as_view(), name="ads-create"),
    path("<int:pk>/", AdventDetail.as_view(), name="ads-detail"),
    path("<int:pk>/delete/", AdventDeleteView.as_view(), name="ads_delete"),
    path("<int:pk>/edit/", AdvertUpdateView.as_view(), name="ads-update"),
    path("statistic/", AdStatisticsView.as_view(), name="add_statistic"),
]
