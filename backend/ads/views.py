from django.db import models
from django.db.models import (
    Count,
    ExpressionWrapper,
    FloatField,
    F,
    Sum,
    Value,
    Case,
    When,
)
from django.db.models.functions import Coalesce
from django.urls import reverse_lazy, reverse
from django.views import View
from rest_framework.request import Request
from django.shortcuts import render
from rest_framework.views import APIView
from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.views.generic import (
    ListView,
    CreateView,
    DetailView,
    DeleteView,
    UpdateView,
)

from .models import Advert
from .forms import AdvertForm


class AdventView(PermissionRequiredMixin, ListView):
    permission_required = "ads.view_advert"
    template_name = "ads/ads-list.html"
    model = Advert
    queryset = Advert.objects.all()
    context_object_name = "ads"


class AdventDetail(PermissionRequiredMixin, DetailView):
    permission_required = "ads.view_advert"
    template_name = "ads/ads-detail.html"
    queryset = Advert.objects.select_related("products")
    context_object_name = "object"


class AdventCreateView(PermissionRequiredMixin, CreateView):
    permission_required = "ads.add_advert"
    model = Advert
    success_url = reverse_lazy("ads:ads-list")
    form_class = AdvertForm

    def form_valid(self, form):
        self.object = form.save()
        response = super().form_valid(form)

        return response


class AdventDeleteView(UserPassesTestMixin, DeleteView):
    def test_func(self):
        return self.request.user.is_superuser

    model = Advert
    success_url = reverse_lazy("ads:ads-list")
    raise_exception = True
    permission_denied_message = "Только администратор может удалять рекламные кампании."


class AdvertUpdateView(PermissionRequiredMixin, UpdateView):
    permission_required = "ads.change_advert"
    model = Advert
    fields = "name", "promotion_path", "budget", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("ads:ads-detail", kwargs={"pk": self.object.pk})


class AdStatisticsView(ListView):
    model = Advert
    template_name = 'ads/ads-statistic.html'
    context_object_name = 'ads'

    def get_queryset(self):
        return Advert.objects.annotate(
            leads_count=Count('leads', distinct=True),
            customers_count=Count('leads__customers', distinct=True),
            total_contract_sum=Coalesce(
                Sum('leads__customers__contract__cost'),
                Value(0, output_field=models.DecimalField(max_digits=10, decimal_places=2))
            ),
            profit=Case(
                When(budget=0, then=Value(None, output_field=FloatField())),
                default=ExpressionWrapper(
                    (F('total_contract_sum') - F('budget')) / F('budget'),
                    output_field=FloatField()
                ),
                output_field=FloatField()
            )
        )
