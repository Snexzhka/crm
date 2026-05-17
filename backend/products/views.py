from django.db.models import Count
from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
)

from .models import Product
from .forms import ProductForm

class ProductListView(PermissionRequiredMixin, ListView):
    permission_required = "products.view_product"
    template_name = "products/products-list.html"
    #model = Product
    queryset = Product.objects.all()
    context_object_name = "products"

class ProductDetailView(PermissionRequiredMixin, DetailView):
    permission_required = "products.view_product"
    template_name = "products/products-detail.html"
    queryset = Product.objects.all()
    context_object_name = "object"


class ProductCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "products.add_product"
    model = Product
    success_url = reverse_lazy("products:product-list")
    form_class = ProductForm

    def form_valid(self, form):

        self.object = form.save()
        response = super().form_valid(form)

        return response


class ProductUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "products.change_product"
    model = Product
    fields = "name", "description", "cost"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("products:product-detail", kwargs={"pk": self.object.pk})

class ProductDeleteView(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_superuser

    model = Product
    success_url = reverse_lazy("products:product-list")
    raise_exception = True
    permission_denied_message = "Только администратор может удалять рекламные кампании."
