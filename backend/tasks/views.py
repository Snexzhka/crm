"""
Представление для создания, удаления и обновления текущих задач,
просмотра списка и деталей задач.
"""
from datetime import timedelta

from django.core.exceptions import PermissionDenied
from django.shortcuts import  redirect
from django.urls import reverse_lazy, reverse
from django.utils import timezone

from django.contrib import messages
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from .forms import TaskForm
from .models import Task


class TaskListView(LoginRequiredMixin, ListView):
    """
    Представление для просмотра списка текущих задач. Для просмотра необходима авторизация.
    """
    template_name = "tasks/tasks-list.html"
    model = Task
    #queryset = Task.objects.select_related("user").filter(is_completed=False)
    context_object_name = "tasks"

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Task.objects.all()
        return Task.objects.filter(user=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_tasks_count'] = Task.objects.filter(
            user=self.request.user,
            is_completed=False,
            due_date__lte=timezone.now().date()
        ).count()
        return context


class TaskDetailView(LoginRequiredMixin, DetailView):
    """
    Представление для просмотра деталей текущих задач. Для просмотра необходима авторизация.
    """
    template_name = "tasks/tasks-detail.html"
    queryset = Task.objects.all()
    context_object_name = "object"

    def get_object(self, queryset=None):
        obj = super().get_object()
        if not (self.request.user.is_superuser or obj.user == self.request.user):
            raise PermissionDenied("У вас нет доступа к этой задаче.")
        return obj


class TaskCreateView(PermissionRequiredMixin, CreateView):
    """
    Представление для создания текущих задач. Необходимы разрешения
    или права админа.
    """
    permission_required = "tasks.add_task"
    raise_exception = True
    model = Task
    success_url = reverse_lazy("tasks:tasks-list")
    form_class = TaskForm

    # def form_valid(self, form):
    #     self.object = form.save()
    #     response = super().form_valid(form)
    #
    #     return response

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class TaskUpdateView(UserPassesTestMixin, UpdateView):
    """
    Представление для обновления текущих задач. Необходимы разрешения
    или права админа.
    """
    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_superuser or obj.user == self.request.user

    model = Task
    fields = "title", "description", "due_date", "is_completed"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("tasks:tasks-detail", kwargs={"pk": self.object.pk})


class TaskDeleteView(UserPassesTestMixin, DeleteView):
    """
    Представление для удаления текущих задач. Необходимы авторизация (быть автором
    задачи) или права админа.
    """
    def test_func(self):
        obj = self.get_object()
        return self.request.user.is_superuser or obj.user == self.request.user

    model = Task
    success_url = reverse_lazy("tasks:tasks-list")


class RescheduleTasksView(LoginRequiredMixin, View):
    """
    Представление для отметки выполнения задач.
    """
    def post(self, request):
        today = timezone.now().date()
        # Находим невыполненные задачи пользователя с due_date <= сегодня
        tasks_to_reschedule = Task.objects.filter(
            user=request.user,
            is_completed=False,
            due_date__lte=today
        )
        count = tasks_to_reschedule.count()
        # Переносим каждую задачу на один день вперёд
        for task in tasks_to_reschedule:
            if task.due_date < today:
                messages.error(request, "Нет задач для переноса")
                return redirect('home')
            task.due_date += timedelta(days=1)
            task.save()
        messages.success(request, f'Перенесено {count} невыполненных задач на завтра.')
        return redirect('tasks:tasks-list')
