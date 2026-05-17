from django.db import models

from products.models import Product



class Advert(models.Model):
    class Meta:
        ordering = ["pk", "name"]

    name = models.CharField(max_length=250)
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    promotion_path = models.CharField(max_length=250)
    budget = models.DecimalField(default=0, decimal_places=2, max_digits=8)

    def __str__(self):
        return f"expenses {self.name!r} - {self.budget}"
