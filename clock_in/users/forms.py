from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import forms, get_user_model
from django.contrib.auth import forms as auth_forms

from django import forms

User = get_user_model()


class UserChangeForm(auth_forms.UserChangeForm):
    class Meta(auth_forms.UserChangeForm.Meta):
        model = User


class UserCreationForm(auth_forms.UserCreationForm):

    error_message = auth_forms.UserCreationForm.error_messages.update(
        {"duplicate_username": _("This username has already been taken.")}
    )

    class Meta(auth_forms.UserCreationForm.Meta):
        model = User

    def clean_username(self):
        username = self.cleaned_data["username"]

        try:
            User.objects.get(username=username)
        except User.DoesNotExist:
            return username

        raise ValidationError(self.error_messages["duplicate_username"])


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User

        fields = [
            "first_name",
            "last_name",
            "day_working_time",
            "time_flexibility",
            "job_position",
            "job_tasks"
        ]

    first_name = forms.CharField(widget=forms.TextInput())
    first_name.label = "Nombre"
    last_name = forms.CharField(widget=forms.TextInput())
    last_name.label = "Apellidos"
    day_working_time = forms.TimeField(widget=forms.TextInput())
    day_working_time.label = "Jornada diaria"
    time_flexibility = forms.BooleanField(widget=forms.CheckboxInput(), required=False)
    time_flexibility.label = "Flexibilidad horaria"
    job_position = forms.CharField(widget=forms.TextInput())
    job_position.label = "Puesto de trabajo"
    job_tasks = forms.CharField(widget=forms.Textarea())
    job_tasks.label = "Tareas encomendadas de forma presencial"



