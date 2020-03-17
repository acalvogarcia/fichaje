import datetime
from calendar import monthrange

from django.db.models import QuerySet
from django.shortcuts import render
from django.views.generic import DetailView, RedirectView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect

from .models import WorkDay, Month, Year

# Create your views here.


class DayDetailView(LoginRequiredMixin, UpdateView):

    model = WorkDay
    fields = [
            "start_time",
            "end_time",
            "lunch_start_time",
            "lunch_end_time",
        ]
    template_name = "days/day_detail.html"

    def get_object(self, **kwargs) -> WorkDay:
        day = self.kwargs["day"]
        month = self.kwargs["month"]
        year = self.kwargs["year"]
        user = self.request.user

        try:
            return WorkDay.objects.get(month__year__user=user, day=day, month__month=month, month__year__year=year)
        except WorkDay.DoesNotExist:
            try:
                year_object = Year.objects.get(user=user, year=year)
            except Year.DoesNotExist:
                year_object = Year.objects.create(user=user, year=year)

            try:
                month_object = Month.objects.get(month=month, year=year_object)
            except Month.DoesNotExist:
                month_object = Month.objects.create(month=month, year=year_object)

            return WorkDay(day=day, month=month_object)

    def post(self, request, **kwargs):
        print(request.__dict__)
        if "_fichar_entrada" in request.POST.keys():
            obj = self.get_object()
            obj.start_time = datetime.datetime.now().time()
            obj.save()
            return HttpResponseRedirect(obj.get_absolute_url())

        if "_fichar_salida" in request.POST.keys():
            obj = self.get_object()
            obj.end_time = datetime.datetime.now().time()
            obj.save()
            return HttpResponseRedirect(obj.get_absolute_url())

        if "_fichar_inicio_comida" in request.POST.keys():
            obj = self.get_object()
            obj.lunch_start_time = datetime.datetime.now().time()
            obj.save()
            return HttpResponseRedirect(obj.get_absolute_url())

        if "_fichar_final_comida" in request.POST.keys():
            obj = self.get_object()
            obj.lunch_end_time = datetime.datetime.now().time()
            obj.save()
            return HttpResponseRedirect(obj.get_absolute_url())

        return super().post(request, **kwargs)


class MonthDetailView(LoginRequiredMixin, ListView):

    model = Month
    template_name = "days/month_detail.html"

    def get_object(self):
        month = self.kwargs["month"]
        year = self.kwargs["year"]
        user = self.request.user

        return Month.objects.get(year__user=user, month=month, year__year=year)

    def get_queryset(self) -> QuerySet:
        month_object = self.get_object()
        return month_object.worked_days.all()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        month = self.kwargs["month"]
        year = self.kwargs["year"]
        user = self.request.user

        days_in_month = [str(num) for num in range(1, monthrange(year, month)[1] + 1)]

        day_working_time = user.day_working_time
        day_working_time_delta = datetime.timedelta(
            hours=day_working_time.hour,
            minutes=day_working_time.minute,
            seconds=day_working_time.second)

        days_worked = {}
        for day in days_in_month:
            try:
                day_object = queryset.get(day=int(day))
                days_worked[day] = {}
                days_worked[day]["day_object"] = day_object
                days_worked[day]["time_worked"] = day_object.time_worked
                days_worked[day]["day_working_time"] = day_working_time_delta
                days_worked[day]["time_balance"] = day_object.time_worked - day_working_time_delta
            except WorkDay.DoesNotExist:
                days_worked[day] = {}
                days_worked[day]["time_worked"] = "--"
                days_worked[day]["day_working_time"] = "--"
                days_worked[day]["time_balance"] = "--"


        # days_worked = {}
        # for day in self.get_queryset():
        #     days_worked[str(day.day)] = {}
        #     days_worked[str(day.day)]["time_worked"] = day.time_worked
        #     day_working_time = user.day_working_time
        #     day_working_time_delta = datetime.timedelta(
        #         hours=day_working_time.hour,
        #         minutes=day_working_time.minute,
        #         seconds=day_working_time.second)
        #     days_worked[str(day.day)]["time_balance"] = day.time_worked - day_working_time_delta

        total_time_worked = datetime.timedelta()
        for time_worked in [day.time_worked for day in self.get_queryset()]:
            total_time_worked += time_worked

        context["days_worked"] = days_worked
        context["days_in_month"] = days_in_month
        context["total_time_worked"] = total_time_worked

        return context


class YearDetailView(LoginRequiredMixin, ListView):

    model = Year
    template_name = "days/year_detail.html"

    def get_queryset(self) -> QuerySet:
        year = self.kwargs["year"]
        user = self.request.user

        return Year.objects.filter(user=user, year=year)
