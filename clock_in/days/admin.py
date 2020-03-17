from django.contrib import admin

from .models import WorkDay, Month, Year

# Register your models here.
@admin.register(WorkDay)
class DayAdmin(admin.ModelAdmin):
    pass

@admin.register(Month)
class MonthAdmin(admin.ModelAdmin):
    pass

@admin.register(Year)
class YearAdmin(admin.ModelAdmin):
    pass
