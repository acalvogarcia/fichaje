import datetime
from calendar import monthrange
from xhtml2pdf import pisa

from django.db.models import QuerySet
from django.shortcuts import render
from django.views.generic import DetailView, RedirectView, UpdateView, ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect, FileResponse, HttpResponse
from django.template.loader import render_to_string

from .models import WorkDay, Month, Year
from .forms import WorkDayForm

# Create your views here.


class DayDetailView(LoginRequiredMixin, UpdateView):

    model = WorkDay
    form_class = WorkDayForm
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
        
        if "_generate_daily_digest_pdf" in request.POST.keys():
            obj = self.get_object()
            obj.save()

            context = {
                "object": obj,
                "daily_digest": obj.digest,
                "user": obj.user,
            }

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Resumen diario {obj.day}-{obj.month.month}-{obj.month.year.year}.pdf"'
            html_string = render_to_string("days/resumen_diario.html", context=context)
            pisa_status = pisa.CreatePDF(
                html_string, dest=response)

            return response 

        return super().post(request, **kwargs)


class MonthDetailView(LoginRequiredMixin, ListView):

    model = Month
    template_name = "days/month_detail.html"

    def get_object(self) -> Month:
        month = self.kwargs["month"]
        year = self.kwargs["year"]
        user = self.request.user

        try:
            return Month.objects.get(month=month, year__year=year)
        except Month.DoesNotExist:
            try:
                year_object = Year.objects.get(user=user, year=year)
            except Year.DoesNotExist:
                year_object = Year.objects.create(user=user, year=year)

            return Month(month=month, year=year_object)

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

        days_worked = {}
        for day in days_in_month:
            days_worked[day] = {}
            try:
                day_object = queryset.get(day=int(day))
                days_worked[day]["day_object"] = day_object
                days_worked[day]["day_link"] = day_object.get_absolute_url
                days_worked[day]["time_worked"] = day_object.time_worked
                days_worked[day]["day_working_time"] = day_object.working_time_delta
                days_worked[day]["time_balance"] = abs(day_object.time_balance)
                days_worked[day]["time_balance_positive"] = day_object.time_balance_positive
            except WorkDay.DoesNotExist:
                days_worked[day]["day_link"] = WorkDay.get_day_url(day=day, month=month, year=year)
                days_worked[day]["time_worked"] = "--"
                days_worked[day]["day_working_time"] = "--"
                days_worked[day]["time_balance"] = "--"
                days_worked[day]["time_balance_positive"] = True

        month_object = self.get_object()

        context["year_link"] = month_object.year.get_absolute_url()
        context["month_link"] = month_object.get_absolute_url()

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

    def get_object(self) -> Year:
        year = self.kwargs["year"]
        user = self.request.user

        return Year.objects.get(user=user, year=year)

    def get_queryset(self) -> QuerySet:
        year = self.kwargs["year"]
        user = self.request.user

        year_object = Year.objects.get(user=user, year=year)
        return year_object.months.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        queryset = self.get_queryset()

        year = self.kwargs["year"]
        user = self.request.user

        months_in_year = [str(num) for num in range(1,13)]

        months_worked = {}
        for month in months_in_year:
            months_worked[month] = {}
            try:
                month_object = queryset.get(month=int(month))
                months_worked[month]["month_object"] = month_object
                months_worked[month]["month_link"] = month_object.get_absolute_url
                months_worked[month]["time_worked"] = month_object.time_worked
                months_worked[month]["month_working_time"] = month_object.working_time_delta
                months_worked[month]["time_balance"] = abs(month_object.time_balance)
                months_worked[month]["time_balance_positive"] = month_object.time_balance_positive
            except Month.DoesNotExist:
                months_worked[month] = {}
                months_worked[month]["month_link"] = Month.get_month_url(month=month, year=year)
                months_worked[month]["time_worked"] = "--"
                months_worked[month]["month_working_time"] = "--"
                months_worked[month]["time_balance"] = "--"
                months_worked[month]["time_balance_positive"] = True
        
        year_object = self.get_object()

        total_time_worked = datetime.timedelta()
        for time_worked in [month.time_worked for month in self.get_queryset()]:
            total_time_worked += time_worked

        context["months_worked"] = months_worked
        context["year_link"] = year_object.get_absolute_url()

        return context
