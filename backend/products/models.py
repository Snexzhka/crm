from django.db import models

class Product(models.Model):
    class Meta:
        ordering = ["name"]

    name = models.CharField(max_length=250)
    description = models.TextField(null=False, blank=True)
    cost = models.DecimalField(default=0, decimal_places=2, max_digits=8)

    def __str__(self):
        return f"Products {self.pk}.{self.name!r} - {self.cost}"
