"""
Представление для контрактов. Предназначено для создания, обновления и
удаления контрактов, просмотра списка контрактов и деталей
"""
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.views.generic import (
    ListView,
    DetailView,
    DeleteView,
    CreateView,
    UpdateView,
)
from .models import Contract
from .forms import ContractForm

class ContractListView(PermissionRequiredMixin, ListView):
    """
    Представление для просмотра списка контактов. Для просмотра необходимо разрешение на просмотр
    или права админа
    """
    permission_required = "contracts.view_contract"
    template_name = "contracts/contracts-list.html"
    model = Contract
    queryset = Contract.objects.all()
    context_object_name = "contracts"


class ContractsDetailView(PermissionRequiredMixin, DetailView):
    """
    Представление для просмотра деталей контактов. Для просмотра необходимо разрешение на просмотр
    или права админа
    """
    permission_required =  "contracts.view_contract"
    template_name = "contracts/contracts-detail.html"
    queryset = Contract.objects.all()
    context_object_name = "object"


class ContractsCreateView(PermissionRequiredMixin, CreateView):
    """
    Представление для создания контактов. Для создания необходимо разрешение на создание
    или права админа
    """
    permission_required =  "contracts.add_contract"
    model = Contract
    success_url = reverse_lazy("contracts:contracts-list")
    form_class = ContractForm

    def form_valid(self, form):
        self.object = form.save()
        print(form.errors)
        response = super().form_valid(form)

        return response

class ContractUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Представление для обновления контактов. Для обновления необходимо разрешение на обновление
    или права админа
    """
    permission_required =  "contracts.change_contract"
    model = Contract
    fields = "name", "products",  "duration", "file", "cost", "lead"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("contracts:contracts-detail", kwargs={"pk": self.object.pk})


class ContractDeleteView(UserPassesTestMixin, DeleteView):
    """
    Представление для удаления контактов. Для удаления необходимы права админа
    """
    def test_func(self):
        return self.request.user.is_superuser

    model = Contract
    success_url = reverse_lazy("contracts:contracts-list")
    raise_exception = True
    permission_denied_message = "Только администратор может удалять рекламные кампании."
