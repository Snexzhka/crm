"""
Модель для создания объектов услуг
"""

from django.db import models


class Product(models.Model):
    """
    Модель для услуг. Содержит название услуги, описание и цену.
    Поля:
        name:название услуги
        description:описание услуги
        cost:цена услуги
    """

    class Meta:
        ordering = ["name"]

    name: models.CharField = models.CharField(max_length=250)
    description: models.TextField = models.TextField(null=False, blank=True)
    cost: models.DecimalField = models.DecimalField(
        default=0, decimal_places=2, max_digits=8
    )

    def __str__(self):
        return f"Products {self.pk}.{self.name!r} - {self.cost}"
