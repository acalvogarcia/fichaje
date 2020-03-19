from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker

from django import forms

from .models import WorkDay

class WorkDayForm(forms.ModelForm):
    class Meta:
        model = WorkDay
        fields = [
            "start_time",
            "end_time",
        ]
    
    start_time = forms.TimeField(widget=forms.TextInput(attrs={"class": "time-input", "width": "30%"}))
    end_time = forms.TimeField(widget=forms.TextInput(attrs={"class": "time-input", "width": "30%"}))
