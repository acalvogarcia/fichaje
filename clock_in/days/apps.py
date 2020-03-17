from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DaysConfig(AppConfig):
    name = 'clock_in.days'
    verbose_name = _("Days")

    def ready(self):
        try:
            import clock_in.days.signals  # noqa F401
        except ImportError:
            pass
