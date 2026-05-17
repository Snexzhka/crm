from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    class Meta:
        ordering = ["pk", "user"]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200)
    department = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.user}  {self.job_title} {self.department}"
