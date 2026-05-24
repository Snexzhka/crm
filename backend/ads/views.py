"""
Представление для вывода данных по рекламным услугам - список, детали услуги, создание,
удаление и обновление услуги.
"""

from django.contrib.auth.mixins import (
    PermissionRequiredMixin,
    UserPassesTestMixin,
)
from django.db import models
from django.db.models import (
    Case,
    Count,
    ExpressionWrapper,
    F,
    FloatField,
    Sum,
    Value,
    When,
)
from django.db.models.functions import Coalesce, Round
from django.urls import reverse, reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import AdvertForm
from .models import Advert


class AdventView(PermissionRequiredMixin, ListView):
    """
    Представление для получения списка рекламных компаний. Для просмотра необходимо
    либо наличие прав на просмотр, либо права админа.
    """

    permission_required = "ads.view_advert"
    template_name = "ads/ads-list.html"
    model = Advert
    queryset = Advert.objects.all()
    context_object_name = "ads"


class AdventDetail(PermissionRequiredMixin, DetailView):
    """
    Представление для получения деталей рекламных компаний. Для просмотра необходимо
    либо наличие прав на просмотр, либо права админа
    """

    permission_required = "ads.view_advert"
    template_name = "ads/ads-detail.html"
    queryset = Advert.objects.select_related("products")
    context_object_name = "object"


class AdventCreateView(PermissionRequiredMixin, CreateView):
    """
    Представление для создания рекламных компаний. Для создания необходимо либо наличие
    прав на создание, либо права админа
    """

    permission_required = "ads.add_advert"
    model = Advert
    success_url = reverse_lazy("ads:ads-list")
    form_class = AdvertForm

    def form_valid(self, form):
        self.object = form.save()  # pylint: disable=attribute-defined-outside-init
        response = super().form_valid(form)

        return response


class AdventDeleteView(UserPassesTestMixin, DeleteView):
    """
    Представление для удаления рекламных компаний. Для удаления необходимо наличие
    прав админа
    """

    def test_func(self):
        return self.request.user.is_superuser

    model = Advert
    success_url = reverse_lazy("ads:ads-list")
    raise_exception = True
    permission_denied_message = "Только администратор может удалять рекламные кампании."

    # def get_permission_denied_message(self):
    #     return "Только администратор может удалять рекламные кампании."


class AdvertUpdateView(PermissionRequiredMixin, UpdateView):
    """
    Представление для обновления рекламных компаний. Для обновления необходимо либо
    наличие прав на обновление, либо права админа
    """

    permission_required = "ads.change_advert"
    model = Advert
    fields = "name", "promotion_path", "budget", "products"
    template_name_suffix = "_update_form"

    def get_success_url(self):
        return reverse("ads:ads-detail", kwargs={"pk": self.object.pk})


class AdStatisticsView(ListView):
    """
    Представление для вывода статистики
    """

    model = Advert
    template_name = "ads/ads-statistic.html"
    context_object_name = "ads"

    def get_queryset(self):
        return Advert.objects.annotate(
            leads_count=Count("leads", distinct=True),
            customers_count=Count("leads__customers", distinct=True),
            total_contract_sum=Coalesce(
                Sum("leads__customers__contract__cost"),
                Value(
                    0, output_field=models.DecimalField(max_digits=10, decimal_places=2)
                ),
            ),
            profit=Case(
                When(budget=0, then=Value(None, output_field=FloatField())),
                default=Round(
                    ExpressionWrapper(
                        (F("total_contract_sum") - F("budget")) / F("budget"),
                        output_field=FloatField(),
                    ),
                    2,
                ),
                output_field=FloatField(),
            ),
        )
