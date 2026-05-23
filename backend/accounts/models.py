from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Profile(models.Model):
    class Meta:
        ordering = ["pk", "user"]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    job_title = models.CharField(max_length=200)
    department = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.user}  {self.job_title} {self.department}"
