from django.urls import path

from .views import DayDetailView, MonthDetailView, YearDetailView

app_name = "users"
urlpatterns = [
    path("<int:year>", YearDetailView.as_view(), name="year"),
    path("<int:year>/<int:month>", MonthDetailView.as_view(), name="month"),
    path("<int:year>/<int:month>/<int:day>", DayDetailView.as_view(), name="day"),
]