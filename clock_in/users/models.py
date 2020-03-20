import datetime

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = models.CharField(_("Name of User"), blank=True, max_length=255)

    day_working_time = models.TimeField(default=datetime.time())
    time_flexibility = models.BooleanField(default=False)

    job_position = models.CharField(max_length=255, blank=True, null=True)
    job_tasks = models.TextField(blank=True, null=True)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def get_month_worked_days(self, month: int = None, year: int = None) -> models.QuerySet:
        month = month if month else datetime.datetime.now().month
        year = year if year else datetime.datetime.now().year

        return self.worked_days.filter(month=month, year=year)
