from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.http import HttpRequest, HttpResponse, request
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views import View
from django.shortcuts import render
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.decorators import login_required

from .models import Profile
from products.models import Product
from ads.models import Advert
from leads.models import Lead
from customers.models import Customer
from tasks.models import Task

@login_required
def home_page(request: HttpRequest):
    """
    Функция для отражения главной страницы
    """
    context = {
        "products_count": Product.objects.count(),
        "ads_count": Advert.objects.count(),
        "leads_count": Lead.objects.count(),
        "customers_count": Customer.objects.count(),
        "tasks_count": Task.objects.count(),
    }
    return render(request, "index.html", context=context)


class LogoutPage(View):
    """
    Представление для выхода из аккаунта
    """
    def get(self, request: HttpRequest):
        logout(request)
        return redirect('accounts:login')

class Messages(TemplateView):
    """
    Представление для вывода сообщения об успешной регистрации
    """
    template_name = "accounts/messages.html"


class RegisterView(CreateView):
    """
    Представление для регистрации пользователей
    """
    form_class = UserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('accounts:message')
    #success_url = "/"

    def form_valid(self, form):
        response = super().form_valid(form)

        Profile.objects.create(user = self.object)
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password1")

        user = authenticate(request=self.request,
                            username=username,
                            password=password,
                            )
        if user is not None:
            login(request=self.request, user=user)
        return response
