from django.contrib import admin
from django.contrib.auth.views import LoginView
from django.urls import path, include


from .views import (
    LogoutPage,
    RegisterView,
    Messages,
)

app_name = "accounts"


urlpatterns = [

    path('login/',
         LoginView.as_view(
             template_name="accounts/login.html",
             redirect_authenticated_user=True,
         ), name="login"),
    path("logout/", LogoutPage.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="registers"),
    path("message/", Messages.as_view(), name="message"),
]