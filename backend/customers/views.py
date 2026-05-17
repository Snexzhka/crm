from django.shortcuts import render
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

from .models import Customer
from .forms import CustomerForm

class CustomerListView(PermissionRequiredMixin, ListView):
    permission_required = "customers.view_customer"
    template_name = "customers/customers-list.html"
    model = Customer
    queryset = Customer.objects.select_related("contract")
    context_object_name = "customers"


class CustomerDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "customers.view_customer"
    template_name = "customers/customers-detail.html"
    queryset = Customer.objects.select_related("lead", "contract")
    context_object_name = "object"


class CustomerCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "customers.add_customer"
    model = Customer
    success_url = reverse_lazy("customers:customers-list")
    form_class = CustomerForm

    def form_valid(self, form):
        self.object = form.save()
        response = super().form_valid(form)

        return response


class CustomerUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "customers.change_customer"
    model = Customer
    fields = "lead", "contract"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("customers:customers-detail", kwargs={"pk": self.object.pk})


class CustomerDeleteView(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_superuser

    model = Customer
    success_url = reverse_lazy("customers:customers-list")
