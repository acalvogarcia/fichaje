from tempus_dominus.widgets import DatePicker, TimePicker, DateTimePicker

from django import forms

from .models import WorkDay

class WorkDayForm(forms.ModelForm):
    class Meta:
        model = WorkDay
        fields = [
            "start_time",
            "end_time",
            "digest",
        ]
    
    start_time = forms.TimeField(widget=forms.TextInput(attrs={"class": "time-input", "width": "30%"}))
    start_time.label = "Hora de entrada"
    end_time = forms.TimeField(widget=forms.TextInput(attrs={"class": "time-input", "width": "30%"}))
    end_time.label = "Hora de salida"
    digest = forms.CharField(widget=forms.Textarea(attrs={"width": "30%"}))
    digest.label = "Resumen diario"
