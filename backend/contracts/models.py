from django.db import models

from products.models import Product


class Contract(models.Model):
    class Meta:
        ordering = ["pk", "name"]

    name = models.CharField(max_length=100)
    products = models.ForeignKey(Product, on_delete=models.CASCADE)
    file = models.FileField(null=True, upload_to="contracts/file")
    start_date = models.DateField(auto_now_add=True)
    duration = models.DurationField()
    cost = models.DecimalField(default=0, max_digits=8, decimal_places=2)
    lead = models.ForeignKey("leads.Lead", on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Лид")
    #profile = models.ForeignKey(Profile, on_delete=models.CASCADE)

    @property
    def end_date(self):
        """Вычисляем дату окончания на основе начала и длительности."""
        return self.start_date + self.duration

    def __str__(self):
        return f"{self.name}-{self.end_date}-{self.cost}"


# duration_days = models.IntegerField()
# @property
# def duration(self):
#     return timedelta(days=self.duration_days)