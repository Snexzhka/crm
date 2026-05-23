"""
Подключение приложения "tasks"
"""

from django.urls import path

from .views import (
    RescheduleTasksView,
    TaskCreateView,
    TaskDeleteView,
    TaskDetailView,
    TaskListView,
    TaskUpdateView,
)

app_name = "tasks"

urlpatterns = [
    path("", TaskListView.as_view(), name="tasks-list"),
    path("rescheduler/", RescheduleTasksView.as_view(), name="tasks-rescheduler"),
    path("<int:pk>/", TaskDetailView.as_view(), name="tasks-detail"),
    path("new/", TaskCreateView.as_view(), name="tasks-create"),
    path("<int:pk>/edit/", TaskUpdateView.as_view(), name="tasks-update"),
    path("<int:pk>/delete/", TaskDeleteView.as_view(), name="tasks-delete"),
]
