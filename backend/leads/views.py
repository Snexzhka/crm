"""
Представления для работы приложения потенциальных клиентов. Реализуют функции
по созданию, обновлению и удалению потенциальных клиентов, просмотр
списка и деталей клиентов.
"""

from django.contrib import messages
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    FormView,
    ListView,
    UpdateView,
)

from customers.models import Customer

from .forms import ConvertLeadForm, ProfileForm
from .models import Lead


class LeadListView(PermissionRequiredMixin, ListView):
    """
    Представление для просмотра списка потенциальных клиентов. Для просмотра
    необходимы права админа или разрешение на просмотр.
    """

    permission_required = "leads.view_lead"
    template_name = "leads/leads-list.html"
    model = Lead
    queryset = Lead.objects.select_related("advert_name")
    context_object_name = "leads"


class LeadDetailView(PermissionRequiredMixin, DetailView):
    """
    Представление для просмотра деталей потенциальных клиентов. Для просмотра
    необходимы права админа или разрешение на просмотр.
    """

    permission_required = "leads.view_lead"
    template_name = "leads/leads-detail.html"
    queryset = Lead.objects.all()
    context_object_name = "object"


class LeadsCreateView(PermissionRequiredMixin, CreateView):
    """
    Представление для создания потенциальных клиентов. Для сощдания
    необходимы права админа или разрешение на создание.
    """

    permission_required = "leads.add_lead"
    model = Lead
    success_url = reverse_lazy("leads:leads-list")
    form_class = ProfileForm

    def form_valid(self, form):
        self.object = form.save()
        response = super().form_valid(form)

        return response


class LeadUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Представление для обновления потенциальных клиентов. Для обновления
    необходимы права админа или разрешение на обновление
    """

    permission_required = "leads.change_lead"
    model = Lead
    fields = "first_name", "last_name", "phone", "email", "advert_name"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("leads:leads-detail", kwargs={"pk": self.object.pk})


class LeadDeleteView(UserPassesTestMixin, DeleteView):
    """
    Представление для удаления потенциальных клиентов. Для удаления необходимы
    права админа.
    """

    def test_func(self):
        return self.request.user.is_superuser

    model = Lead
    success_url = reverse_lazy("leads:leads-list")
    raise_exception = True
    permission_denied_message = "Только администратор может удалять рекламные кампании."


class ConvertLeadView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    """
    Представление для перевода из списка потенциальных клиентов в список активных
    клиентов. Необходимы права админа или разрешение.
    """

    template_name = "leads/convert_lead.html"
    form_class = ConvertLeadForm
    success_url = reverse_lazy("customers:customers-list")
    permission_required = "customers.add_customer"
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        self.lead = get_object_or_404(Lead, pk=kwargs["pk"])
        if Customer.objects.filter(lead=self.lead).exists():
            messages.info(request, "Этот лид уже является активным клиентом.")
            return redirect("leads:leads-detail", pk=self.lead.pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["lead"] = self.lead
        return kwargs

    def form_valid(self, form):
        contract = form.cleaned_data["contract"]
        Customer.objects.create(lead=self.lead, contract=contract)
        return redirect("customers:customers-list")

    def get_success_url(self):
        return reverse("customers:customers-list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["lead"] = self.lead
        return context
