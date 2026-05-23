"""
Модель для приложения "leads"
"""
from django.db import models


class Lead(models.Model):
    """
    Модель для создания объектов потенциальных клиентов. Содержит поля
    ФИО, телефон, емайл, связь с рекламной компанией.
    Поля:
        first_name:имя
        last_name:фамилия
        phone:телефон
        email:емайл
        advert_name:связь с таблицей рекламы
    """
    class Meta:
        ordering = ["pk", "first_name"]

    first_name: models.CharField = models.CharField(max_length=100)
    last_name: models.CharField = models.CharField(max_length=150, null=True, blank=True)
    phone: models.CharField = models.CharField(max_length=20)
    email: models.EmailField = models.EmailField(null=False, blank=True)
    advert_name: models.ForeignKey['Advert'] = models.ForeignKey(
        "ads.Advert", on_delete=models.SET_DEFAULT,
        default="without_adverting",
        related_name="leads")

    @property
    def has_customer(self):
        from customers.models import Customer
        return Customer.objects.filter(lead=self).exists()

    def __str__(self):
        return f"{self.first_name}, {self.last_name}, {self.phone}, {self.email}"
