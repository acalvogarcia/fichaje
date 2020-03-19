import datetime

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

# Create your models here.


def substract_times(end_time, start_time):
    start_time_delta = datetime.timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)
    end_time_delta = datetime.timedelta(hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second)
    return end_time_delta - start_time_delta


class Year(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='worked_days')
    year = models.IntegerField()

    unique_together = ['year', 'user']

    def get_absolute_url(self):
        return reverse("days:year", kwargs={"year": self.year})


class Month(models.Model):
    month = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)])
    year = models.ForeignKey(Year, on_delete=models.CASCADE, related_name='months')

    unique_together = ['month', 'year']
    
    @property
    def user(self) -> User:
        return self.year.user
    
    @property
    def time_worked(self) -> datetime.timedelta:
        time_worked = datetime.timedelta(0)
        for day in self.worked_days.all():
            time_worked += day.time_worked
        return time_worked
    
    @property
    def working_time_delta(self) -> datetime.timedelta:
        day_working_time = self.user.day_working_time
        day_working_time_delta = datetime.timedelta(
            hours=day_working_time.hour,
            minutes=day_working_time.minute,
            seconds=day_working_time.second)
        return self.worked_days.count() * day_working_time_delta
    
    @property
    def time_balance(self) -> datetime.timedelta:
        time_balance = datetime.timedelta(0)
        for day in self.worked_days.all():
            time_balance += day.time_balance
        return time_balance

    @property
    def time_balance_positive(self) -> bool:
        return self.time_balance >= datetime.timedelta(0)

    @classmethod
    def get_month_url(cls, month, year):
        return reverse("days:month", kwargs={"month": month, "year": year})

    def get_absolute_url(self):
        return reverse("days:month", kwargs={"month": self.month, "year": self.year.year})


class WorkDay(models.Model):

    day = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(31)])
    month = models.ForeignKey(Month, on_delete=models.CASCADE, related_name='worked_days')

    start_time = models.TimeField(blank=True, null=True)
    end_time = models.TimeField(blank=True, null=True)

    lunch_start_time = models.TimeField(blank=True, null=True)
    lunch_end_time = models.TimeField(blank=True, null=True)

    unique_together = ['day', 'month']

    @property
    def user(self) -> User:
        return self.month.year.user

    @property
    def time_worked(self) -> datetime.timedelta:
        if not self.start_time or not self.end_time:
            raise ValueError("Both start_time and end_time must be set in order to calculate the worked time")
        start_time = self.start_time
        end_time = self.end_time

        start_time_delta = datetime.timedelta(hours=start_time.hour, minutes=start_time.minute, seconds=start_time.second)
        end_time_delta = datetime.timedelta(hours=end_time.hour, minutes=end_time.minute, seconds=end_time.second)
        time_elapsed = end_time_delta - start_time_delta

        if self.lunch_start_time and self.lunch_end_time:
            lunch_time_delta = substract_times(self.lunch_end_time, self.lunch_start_time)
            return time_elapsed - lunch_time_delta

        return time_elapsed

    @property
    def working_time_delta(self) -> datetime.timedelta:
        day_working_time = self.user.day_working_time
        return datetime.timedelta(
            hours=day_working_time.hour,
            minutes=day_working_time.minute,
            seconds=day_working_time.second)

    @property
    def time_balance(self) -> datetime.timedelta:
        courtesy_time = datetime.timedelta(0)
        user = self.user
        start_time_limit = datetime.time(hour=10) if user.time_flexibility else datetime.time(hour=9)
        end_time_limit = datetime.time(hour=14)
        if self.start_time < start_time_limit:
            courtesy_time += datetime.timedelta(minutes=10)
        if self.end_time > end_time_limit:
            courtesy_time += datetime.timedelta(minutes=10)
        return self.time_worked + courtesy_time - self.working_time_delta
    
    @property
    def time_balance_positive(self) -> bool:
        return self.time_balance >= datetime.timedelta(0)

    @classmethod
    def get_day_url(cls, day: int, month:int , year: int):
        return reverse("days:day", kwargs={"day": day, "month": month, "year": year})

    def get_absolute_url(self):
        return reverse("days:day", kwargs={"day": self.day, "month": self.month.month, "year": self.month.year.year})
