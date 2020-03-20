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
    
    start_time = forms.TimeField(widget=forms.TextInput(attrs={"class": "time-input", "width": "30%"}), required=False)
    start_time.label = "Hora de entrada"
    end_time = forms.TimeField(widget=forms.TextInput(attrs={"class": "time-input", "width": "30%"}), required=False)
    end_time.label = "Hora de salida"
    digest = forms.CharField(widget=forms.Textarea(attrs={"width": "30%"}), required=False)
    digest.label = "Resumen diario"
